import socket, threading, time
import sys
from _thread import *

log = []
tt = [[0,0,0],[0,0,0],[0,0,0]]

votes = {"A": 0, "B": 0}
voteLock = threading.Lock()

def sendUpdate():
    global log
    global tt
    global serverID
    sendServerID = str((serverID + 1) % 3)
    initMessage = "serverNum:" + sendServerID

    sendIP = input("Please enter the IP address of server " + sendServerID + ": ")
    sendPort = int(input("Please enter the port of server " + sendServerID + ": "))

    sendSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sendSocket.connect((sendIP, sendPort))
    sendSocket.sendall(initMessage.encode())

def recvUpdate():

    global serverID
    serverListener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverListener.bind(("127.0.0.1", (8000 + serverID)))
    serverListener.listen(1)

    connection, address = serverListener.accept()
    data = connection.recv(1024).decode()

    recvID = data.split(":")[1]
    assert serverID == recvID

    print(data)

def Main():
    global log
    global tt
    global serverID

    serverID = 3
    while (serverID > 2):
        serverID = int(input("Please enter server ID: "))
        if (serverID > 2):
            print("Error: Only 3 servers permitted. Server ID must be 0, 1, or 2.")

    start_new_thread(recvUpdate, ())
    start_new_thread(sendUpdate, ())

    time.sleep(10) #Fix later
    vote = ""
    while True:
        vote = input("Please enter A to vote for Alice, and B to vote for Bob (or Q to to quit): ")

        if vote == "Q":
            break
        elif vote == "A" or vote == "B":
            voteLock.acquire()
            votes[vote] += 1
            vote = "Vote:" + vote
            log.append(vote)
            voteLock.release()
        else:
            print("Error: Invalid input.")


if __name__ == "__main__":
    Main()
