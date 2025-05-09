import socket
import threading
import random
import time

# Configuration
serverIP = "127.0.0.1"
TCPPort = 6000
UDPPort = 6001
MIN_PLAYERS = 2
MAX_PLAYERS = 4
game_duration = 60
GUESS_RANGE = (1, 100)
WAIT_TIME = 10  # seconds to wait after the second player joins

active_clients = {}  # Map: socket -> player name
udp_mapping = {}     # Map: UDP address -> player name
game_active = False
complete_flag = False
secret_number = random.randint(GUESS_RANGE[0], GUESS_RANGE[1])

# Create TCP and UDP server sockets
tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tcp_server_socket.bind((serverIP, TCPPort))
udp_server_socket.bind((serverIP, UDPPort))
tcp_server_socket.listen(5)

# Display server start message
print(f"Server started on {serverIP}: TCP {TCPPort}, UDP {UDPPort}")
print("Connection established. Waiting for players...")

def accept_clients():
    while True:
        conn, addr = tcp_server_socket.accept()
        if game_active:
            conn.send(b"Game in progress. Please wait for the next round.\n")
            conn.close()
            continue
        threading.Thread(target=handle_client, args=(conn, addr)).start()

def handle_client(conn, addr):
    global game_active
    try:
        conn.send(b"Welcome to the game! Please send: JOIN <your_name>\n")
        data = conn.recv(1024).decode().strip()
        if data.startswith("JOIN "):
            player_name = data.split(" ")[1]
            if player_name in active_clients.values():
                conn.send(b"Name already used. Please try again.\n")
                conn.close()
                return
            
            active_clients[conn] = player_name
            print(f"{player_name} joined from {addr}")

            # Broadcast waiting room status
            broadcast(f"Waiting Room: {', '.join(active_clients.values())}\n")

            # Start the game automatically after WAIT_TIME if at least MIN_PLAYERS are in
            if len(active_clients) == MIN_PLAYERS:
                threading.Thread(target=start_after_delay).start()
            elif len(active_clients) == MAX_PLAYERS:
                start_round()

        else:
            conn.send(b"Invalid join command. Disconnecting.\n")
            conn.close()

        # Monitor for client disconnection
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    raise ConnectionResetError  # Trigger disconnection handling
            except:
                handle_disconnection(conn)
                break

    except Exception as e:
        print(f"Error handling client: {e}")
        handle_disconnection(conn)

def handle_disconnection(conn):
    """Handles client disconnection gracefully"""
    global game_active
    if conn in active_clients:
        player_name = active_clients[conn]
        print(f"Player '{player_name}' has disconnected from the game!")
        broadcast(f"Player '{player_name}' has disconnected from the game!\n")
        del active_clients[conn]

        # Check if only one player remains
        if len(active_clients) == 1 and game_active:
            remaining_player = list(active_clients.keys())[0]
            # Send the continuation prompt only to the remaining player
            try:
                remaining_player.send(f"**{player_name} decided to leave you alone in this game, do you want to continue? Yes/No\n".encode())
            except:
                print(f"Error sending continuation prompt to {active_clients[remaining_player]}")

        elif len(active_clients) == 0:
            print("No players remaining. Game ended.")
            game_active = False
            complete_flag = False


def start_after_delay():
    time.sleep(WAIT_TIME)
    if not game_active and len(active_clients) >= MIN_PLAYERS:
        start_round()

def start_round():
    global game_active, secret_number, complete_flag
    game_active = True
    complete_flag = False
    secret_number = random.randint(GUESS_RANGE[0], GUESS_RANGE[1])
    print(f"Secret number is {secret_number}")

    # Display the number of players before the game starts
    print(f"Starting game with {len(active_clients)} players...\n")

    start_msg = f"Game started with {len(active_clients)} players.\nYou have 60 seconds to guess the number ({GUESS_RANGE[0]}-{GUESS_RANGE[1]})!\n"
    broadcast(start_msg)
    threading.Thread(target=handle_guesses).start()

def handle_guesses():
    global game_active, complete_flag
    end_time = time.time() + game_duration
    while time.time() < end_time:
        if complete_flag:
            return
        try:
            guess_data, client_addr = udp_server_socket.recvfrom(1024)
            guess = guess_data.decode().strip()

            # Correctly map UDP address to player name
            if client_addr not in udp_mapping:
                for conn, name in active_clients.items():
                    # Map using the player's TCP socket address to ensure accuracy
                    if conn.getpeername()[0] == client_addr[0]:
                        udp_mapping[client_addr] = name
                        break

            guess = int(guess)
            player_name = udp_mapping.get(client_addr, "Unknown")

            # Handle out-of-range guess
            if guess < GUESS_RANGE[0] or guess > GUESS_RANGE[1]:
                print(f"Send Warning to {player_name}")
                udp_server_socket.sendto(b"Warning: Out of the range, miss your chance\n", client_addr)
                continue

            # Provide feedback
            if guess < secret_number:
                udp_server_socket.sendto(b"Higher\n", client_addr)
            elif guess > secret_number:
                udp_server_socket.sendto(b"Lower\n", client_addr)
            else:
                complete_flag = True
                game_result(client_addr)
                return
        except:
            continue

    if not complete_flag:
        broadcast("Time is up! No Winner.\n")
        complete_flag = False
        game_active = False

def game_result(winner_addr):
    global game_active
    # Fetch the correct player name from the mapping
    winner_name = udp_mapping.get(winner_addr, "Unknown")
    result_msg = f"GAME RESULT\nTarget number was: {secret_number}\nWinner: {winner_name}\n"
    broadcast(result_msg)
    print(f"Game Completed. Winner: {winner_name}\n")
    game_active = False

def broadcast(message):
    for conn in list(active_clients.keys()):
        try:
            conn.send(message.encode())
        except:
            conn.close()

if __name__ == "__main__":
    threading.Thread(target=accept_clients).start()
