from socket import *
from threading import *
import time
import random

#Malak Milhem && Taymaa Nasser
#student ID = 1222640
serverPort = 9960
serverName = "game main server"
server_socket = socket(AF_INET, SOCK_DGRAM) #UDP
serverSocket = socket(AF_INET,SOCK_STREAM) #TCP