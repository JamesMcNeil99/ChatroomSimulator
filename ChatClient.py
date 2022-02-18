#Name:    James Tyler McNeil
#Course:  CSCI 4335
#Date:    3/18/2020



from socket import *
import select
from threading import *
chatVersion = "CHAT/1.0"
serverName = '127.0.0.1'
serverPort = 12000
#variable that governs the thread that receives incoming messages
global isRunning
isRunning = True

#function to count the number of words in a message
def getNumOfWords(s):
    s = s.strip()
    sa = s.split(" ")
    return len(sa)

#thread function to wait for incoming messages from the server
def checkForOutput(clientSocket):
    while(isRunning):
        is_readable = [clientSocket]
        is_writable = []
        is_error = []
        r, w, e = select.select(is_readable,is_writable,is_error, 1.0)
        if r:
            response = clientSocket.recv(1024).decode()
            response = response.splitlines()
            x = 2
            while x < len(response):
                print(response[x])
                x += 1
    return



clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))



#gets name from user, sends JOIN message to server
name = input("Type your user name: ")
name = name.strip()
message = chatVersion + "\n" + "JOIN\n" + "Username: " + name
clientSocket.send(message.encode())
#gets server response to join
response = clientSocket.recv(1024).decode()
response = response.splitlines()
#prints welcome message
x = 2
while x < len(response):
    print(response[x])
    x += 1

#starts thread to listen for incoming messages from the server
t = Thread(target = checkForOutput, args=(clientSocket,))
t.start()

#loops until user types \leave, waits for new input to send to the server
output = ""
while output != "\\leave":
    output = input()
    is_readable = []
    is_writable = [clientSocket]
    is_error = []
    r, w, e = select.select(is_readable,is_writable,is_error, 1.0)
    if w and output != "\\leave":
        message = chatVersion + "\n" + "TEXT\n" + "Username: " + name + "\n" + "Length: " + str(getNumOfWords(output)) + "\n" + output
        clientSocket.send(message.encode())
#closes thread
isRunning = False
t.join()
#sends LEAVE message to server
message = chatVersion + "\n" + "LEAVE\n" + "Username: " + name
clientSocket.send(message.encode())
#receives farewell from server, closes connection
response = clientSocket.recv(1024).decode()
response = response.splitlines()
print(response[2])
clientSocket.close()