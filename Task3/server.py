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
Player_1 = "Milhem_Malak"
Player_2 = "Nasser_Taymaa"
##TCP connection:
TCPPort = 6000
serverSocket = socket(AF_INET,SOCK_STREAM) #TCP

##UDP connection:
UDPPort = 6001
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP
server_socket.bind((serverIP, UDPPort))

generate_random_num


def start_round():
