import socket, threading, time
from _thread import *

log = []
tt = [[0,0,0],[0,0,0],[0,0,0]]

votes = {"A": 0, "B": 0}
voteLock = threading.Lock()
printLock = threading.Lock()

def sendUpdate():

    global log
    global tt
    global serverID

    sendServerID = str((serverID + 1) % 3)
    initMessage = "serverNum:" + sendServerID

    sendIP = input("Please enter the IP address of server " + sendServerID + ": ")
    sendPort = int(input("Please enter the port of server " + sendServerID + ": "))
    printLock.release()

    sendSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sendSocket.connect((sendIP, sendPort))
    sendSocket.sendall(initMessage.encode())

    #while True:
        ##Create a message containing log and timetable
        #time.sleep(3)
        #sendSocket.sendall(message.encode())

def recvUpdate():

    global serverID

    serverListener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverListener.bind(("127.0.0.1", (8000 + serverID)))
    serverListener.listen(1)

    connection, address = serverListener.accept()
    data = connection.recv(1024).decode()

    recvID = data.split(":")[1]
    # assert recvID == serverID

    #while True:
        #data = recv(1024).decode()
        #if not data:
            #break
        ##Extract log and timetable from data
        #voteLock.acquire()
        ##Update log, dictionary, and time table
        #voteLock.release()

def Main():
    global log
    global tt
    global serverID

    serverID = int(input("Please enter server ID: "))

    while (serverID > 2):
        serverID = int(input("Error: Only 3 servers permitted. Please enter a valid server ID (0, 1, or 2): "))

    printLock.acquire()
    start_new_thread(recvUpdate, ())
    start_new_thread(sendUpdate, ())

    printLock.acquire()
    while True:
        vote = input("Please enter A to vote for Alice, and B to vote for Bob (or Q to to quit): ")

        if vote == "A" or vote == "B":
            voteLock.acquire()

            votes[vote] += 1
            vote = "Vote:" + vote
            log.append(vote)
            tt[serverID][serverID] += 1

            voteLock.release()
        elif vote == "Q":
            break
        else:
            print("Error: Invalid input.")
    printLock.release()


if __name__ == "__main__":
    Main()
