import socket
import threading
import time

serverIP = "127.0.0.1"
TCPPort = 6000
UDPPort = 6001
game_duration = 60

# Client state management
game_active = False
game_over = False

# Create UDP socket for receiving feedback
UDP_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDP_client_socket.bind(("0.0.0.0", 0))  # Bind to any available port

def print_header(player_name):
    print(f"\n{'='*30}")
    print(f"  Connected as {player_name}")
    print("  UDP connection established")
    print(f"{'='*30}\n")

def register_player(tcp_socket):
    while True:
        username = input("Enter your username: ").strip()
        tcp_socket.send(f"JOIN {username}".encode())
        response = tcp_socket.recv(1024).decode().strip()
        if "Name already used" in response:
            print(f"Server (TCP): {response}")
            print("="*30)
            print("Username already taken. Try again.\n")
        else:
            print_header(username)
            return username

def listen_for_feedback(tcp_socket):
    global game_active, game_over
    while True:
        try:
            message = tcp_socket.recv(1024).decode().strip()
            if message:
                # Detect game start
                if "Game started" in message:
                    game_active = True
                    game_over = False
                    print(f"Server (TCP): {message}")
                    print("="*30)

                # Detect game result and end
                elif "GAME RESULT" in message:
                    game_active = False
                    game_over = True
                    print(f"Server (TCP): {message}")
                    print("Game has ended. Waiting for the next round...")
                    print("="*30)

                # Handle player disconnection mid-game
                elif "decided to leave you alone" in message:
                    print(f"Server (TCP): {message}")
                    print("="*30)
                    choice = input("Do you want to continue? Yes/No: ").strip().lower()
                    if choice == "yes":
                        print("Continuing the game as a single player...")
                        game_active = True  # Keep the game running
                        print("="*30)
                    else:
                        print("Game ended by player choice.")
                        game_active = False
                        game_over = True
                        break

                # General server messages
                else:
                    print(f"Server (TCP): {message}")
                    print("="*30)

        except Exception as e:
            print(f"TCP connection lost: {e}")
            break

def listen_for_udp_feedback():
    global game_over
    while True:
        try:
            if game_over:
                return
            feedback, _ = UDP_client_socket.recvfrom(1024)
            print(f"Feedback: {feedback.decode().strip()}")
            print("="*30)
        except Exception as e:
            print(f"UDP feedback error: {e}")
            break


def send_guesses():
    while True:
        try:
            if game_active and not game_over:
                guess = input("Enter your guess (1-100): ")
                if guess.isdigit():
                    print(f"\nYour guess: {guess}")
                    UDP_client_socket.sendto(guess.encode(), (serverIP, UDPPort))
                else:
                    print("Invalid input. Please enter a number.")
                print("="*30)  # Divider after guess input
            else:
                time.sleep(1)  # Wait for the game to start
        except Exception as e:
            print(f"Error sending guess: {e}")

def main():
    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((serverIP, TCPPort))

        # Register player with username handling
        username = register_player(tcp_socket)

        # Start TCP and UDP feedback listeners
        threading.Thread(target=listen_for_feedback, args=(tcp_socket,), daemon=True).start()
        threading.Thread(target=listen_for_udp_feedback, daemon=True).start()

        # Start the guessing function in the main thread
        send_guesses()

    except socket.error as e:
        print(f"Socket error: {e}")
    finally:
        print("Client shutting down.")
        tcp_socket.close()
        UDP_client_socket.close()

if __name__ == "__main__":
    main()
