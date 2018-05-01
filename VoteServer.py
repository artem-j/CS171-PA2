import socket, threading, time
import pickle
from _thread import *

log = []
tt = [[0,0,0],[0,0,0],[0,0,0]]

connectionMap = {0:True, 1:True, 2:True}
votes = {"A": 0, "B": 0}
voteLock = threading.Lock()
printLock = threading.Lock()

def sendUpdate():

    global log
    global tt
    global serverID

    sendIP = input("Please enter the IP address of server " + sendServerID + ": ")
    sendPort = int(input("Please enter the port of server " + sendServerID + ": "))
    printLock.release()

    sendSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sendSocket.connect((sendIP, sendPort))

    while True:
        if (connectionMap[serverID]):
            package = [log, tt]
            message = pickle.dumps(package)
            time.sleep(3)
            sendSocket.sendall(message)
            print("Update message sent to " + sendServerID)

def recvUpdate():

    global serverID
    global serverPort

    prevServerID = (serverID - 1) % 3
    serverListener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverListener.bind(("127.0.0.1", serverPort))
    serverListener.listen(1)

    connection, address = serverListener.accept()

    while True:
        data = connection.recv(1024)
        if not data:
            break

        print("Update message received from " + str(prevServerID))

        remotePkg = pickle.loads(data)
        remoteLog = remotePkg[0]
        remoteTT = remotePkg[1]

        voteLock.acquire()

        for r in remoteLog:
            if r not in log:
                timestamp, candidate = r.split(":")
                server, time = timestamp.split(".")
                if tt[serverID][int(server)] < int(time):
                    votes[candidate] += 1
                    log.append(r)

        for i in range(0,3):
            for j in range(0,3):
                if remoteTT[i][j] > tt[i][j]:
                    tt[i][j] = remoteTT[i][j]

        for k in range(0,3):
            if remoteTT[prevServerID][k] > tt[serverID][k]:
                tt[serverID][k] = remoteTT[prevServerID][k]

        trashcan = []

        for l in range(0,3):
            gcTime = min(tt[0][l], tt[1][l], tt[2][l])
            for r in log:
                server, timestamp = r.split(":")[0].split(".")
                if server == str(l) and int(timestamp) <= gcTime:
                    trashcan.append(r)

        for garbage in trashcan:
            log.remove(garbage)

        voteLock.release()

def Main():

    global log
    global tt
    global serverID
    global sendServerID
    global serverPort

    serverID = int(input("Please enter local server ID: "))
    sendServerID = str((serverID + 1) % 3)

    serverPort = int(input("Please enter local port: "))

    while (serverID > 2):
        serverID = int(input("Error: Only 3 servers permitted. Please enter a valid server ID (0, 1, or 2): "))

    printLock.acquire()
    start_new_thread(recvUpdate, ())
    start_new_thread(sendUpdate, ())

    printLock.acquire()
    while True:
        print("Please select one of the following options:\n"
              "A: Vote for Alice\nB: Vote for Bob\n"
              "T: Terminate outgoing link\nR: Restore outgoing link\n"
              "P: Print current local state\nQ: Quit")
        vote = input("Enter selection: ")

        if vote == "A" or vote == "B":
            voteLock.acquire()

            votes[vote] += 1
            tt[serverID][serverID] += 1
            vote = str(serverID) + "." + str(tt[serverID][serverID]) + ":" + vote
            log.append(vote)

            voteLock.release()
        elif vote == "T":
            connectionMap[serverID] = False
            print("Closed link from " + str(serverID) + " to " + sendServerID)
        elif vote == "R":
            connectionMap[serverID] = True
            print("Restored link from " + str(serverID) + " to " + sendServerID)
        elif vote == "P":
            print("\nCurrent votes:")
            print(votes)
            print("Current Timetable:")
            for i in range(0,3):
                print(tt[i])
            print("Current log:")
            print(str(log) + "\n")
        elif vote == "Q":
            break
        else:
            print("Error: Invalid input.")

    printLock.release()


if __name__ == "__main__":
    Main()
