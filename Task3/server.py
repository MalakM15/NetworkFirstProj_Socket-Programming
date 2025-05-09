from socket import *
from threading import *
import time
import random
import collections

#Taymaa Nasser  &&  Malak Milhem
#
MIN_PLAYERS=2
MAX_PLAYERS=4
game_duration = 60  # seconds
GUESS_TIME = 10   # seconds
GUESS_RANGE = (1, 100)
#serverName = "game main server"
serverIP = "127.0.0.1"
player_names = {
    "Player_1": "Milhem_Malak",
    "Player_2": "Nasser_Taymaa"
}
##TCP connection:
TCPPort = 6000
tcp_server_socket = socket(AF_INET, SOCK_STREAM) #TCP
tcp_server_socket.bind((serverIP, TCPPort))
tcp_server_socket.listen()
##UDP connection:
UDPPort = 6001
udp_server_socket = socket(AF_INET, SOCK_DGRAM) #UDP
udp_server_socket.bind((serverIP, UDPPort))

active_clients = {}
complete_flag = False

def generate_random_num():
    return random.randint(*GUESS_RANGE)

def handle_client(connection, address):
    try:
        connection.send(b"Welcome to the game! Please send: JOIN <your_name>\n")
        data = connection.recv(1024).decode().strip()
        if data.startswith("JOIN"):
            _, name = data.split(" ", 1)
            if name in active_clients.values():
                connection.send(b"Name already used. Use another name.\n")
                connection.close()
                return
            active_clients[connection] = name
            print(f"{name} joined from {address}")
            connection.send(b"Signed Successfully. Waiting for others...\n")
        else:
            connection.send(b"Invalid response. Connection closing.\n")
            connection.close()
    except:
        if connection in active_clients:
            print(f"{active_clients[connection]} disconnected from the game!!.")
            del active_clients[connection]
            for conn in active_clients:
                try:
                    conn.send(f"{active_clients[connection]} has decided to leave you alone in the game.\n".encode())
                except:
                    continue
        connection.close()


def handle_guesses(secret_number):

    global complete_flag
    end_time = time.time() + game_duration
    while time.time() < end_time:
    
        try:
            udp_data, client_addr = udp_server_socket.recvfrom(1024)
            guess_msg = udp_data.decode().strip()
            if not guess_msg.isdigit():
                udp_server_socket.sendto(b"Invalid guess. Must be a number.\n", client_addr)
                continue

            guess = int(guess_msg)
            if guess < GUESS_RANGE[0] or guess > GUESS_RANGE[1]:
                udp_server_socket.sendto(b"Warning: Out of the range, miss your chance\n", client_addr)
                continue

            if guess < secret_number:
                udp_server_socket.sendto(b"Higher\n", client_addr)
            elif guess > secret_number:
                udp_server_socket.sendto(b"Lower\n", client_addr)
            else:
                udp_server_socket.sendto(b"Correct!\n", client_addr)
                complete_flag = True
                game_result(client_addr) #the winner
                return

        except:
            continue
    if not complete_flag:
        for connection in active_clients:
            connection.send(b"Time is up! No Winner.\n") 
        tcp_server_socket.close()
        udp_server_socket.close()       

def accept_clients():
    while True:
        conn, addr = tcp_server_socket.accept()
        Thread(target=handle_client, args=(conn, addr)).start()


def game_result(winner_address):
    winner_name = None
    for connection, name in active_clients.items(): ##to find the winner IP
        if connection.getpeername()[0] == winner_address[0]:
           winner_name = name
           break
    if winner_name:       
        print_result = f" GAME RESULT\n Target number was: {secret_number}\n Winner:{winner_name}\n".encode()
    else :
        print_result = f"GAME Completed\n Target number was: {secret_number}\n ".encode()
    #
    for connection in active_clients:
        connection.send(print_result)
        connection.close()
    tcp_server_socket.close()
    udp_server_socket.close()
    print(f"Game Completed. Winner:{winner_name}.\n")

def start_round():
    global guess_start_time

    while len (active_clients)< MIN_PLAYERS:
        print ("Waiting for Players ...\n")
        time.sleep(5)
    print("Minimum players reached, get ready.\n ")
    start_msg = f"Game started with {len(active_clients)} players. \n You have 60 seconds to guess the number between {GUESS_RANGE[0]} and {GUESS_RANGE[1]}!\n".encode()
    for conn in active_clients:
        conn.send(start_msg)  #send the start messege for all clients

    global secret_number 
    secret_number = generate_random_num()
    print(f"Secret number is {secret_number}")
    guess_start_time = time.time()

    # Start UDP guessing listen
    Thread(target=handle_guesses, args=(secret_number,)).start()
    time.sleep(game_duration + 5)  # Wait to finish and start new round 

def main():
        
        print("Connection established. Waiting for players...")
        Thread(target=accept_clients).start()
        Thread(target=start_round).start()     

if __name__ == "__main__":
    main()        
