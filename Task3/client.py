##Task3: client
##Taymaa Nasser  &&  Malak Milhem
import socket
import threading
import time

serverIP = "127.0.0.1"
TCPPort = 6000
UDPPort = 6001

game_duration = 60  # seconds
GUESS_TIME = 10   # seconds
GUESS_RANGE = (1, 100)




UDP_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def guesses(UDP_socket):
    start_time = time.time()
    while time.time() - start_time < game_duration:
        try:
            guess = input (f"Enter your guess({GUESS_RANGE[0]}-{GUESS_RANGE[1]}):")
            guess = guess.strip()
            if guess.isdigit():
                UDP_socket.sendto(guess.encode(), (serverIP, UDPPort))
            else:
                print("Please enter a valid integer.")
            time.sleep(GUESS_TIME)
        except:
            break            

def main():

    try:
        TCP_client_socket = socket(AF_INET, SOCK_STREAM)
        TCP_client_socket.connect((serverIP, TCPPort))




if __name__ == "__main__":
    main()