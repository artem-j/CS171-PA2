import socket, threading, time
import pickle
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

    while True:
        package = [log, tt]
        message = pickle.dumps(package)
        time.sleep(3)
        sendSocket.sendall(message)

def recvUpdate():

    global serverID

    prevServerID = (serverID - 1) % 3
    serverListener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverListener.bind(("127.0.0.1", (8000 + serverID)))
    serverListener.listen(1)

    connection, address = serverListener.accept()
    data = connection.recv(1024).decode()

    # recvID = data.split(":")[1]
    # assert recvID == serverID

    while True:
        data = connection.recv(1024)
        if not data:
            break

        remotePkg = pickle.loads(data)
        remoteLog = remotePkg[0]
        remoteTT = remotePkg[1]

        voteLock.acquire()

        for v in remoteLog:
            if v not in log:
                time, candidate = v.split(":")
                votes[candidate] += 1
                log.append(v)

        for i in range(0,3):
            for j in range(0,3):
                if remoteTT[i][j] > tt[i][j]:
                    tt[i][j] = remoteTT[i][j]

        for k in range(0,3):
            if remoteTT[prevServerID][k] > tt[serverID][k]:
                tt[serverID][k] = remoteTT[prevServerID][k]

        #print("Current TT:")
        #for n in range(0,3):
        #    print(tt[n])

        voteLock.release()

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
            tt[serverID][serverID] += 1
            vote = str(tt[serverID][serverID]) + ":" + vote
            log.append(vote)

            voteLock.release()
        elif vote == "Q":
            break
        else:
            print("Error: Invalid input.")

    printLock.release()


if __name__ == "__main__":
    Main()
