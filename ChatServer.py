#Name:    James Tyler McNeil
#Course:  CSCI 4335
#Date:    3/18/2020


from threading import *
from socket import *
import select


chatVersion = "CHAT/1.0"
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen()

#variable used to track chat history
userDict = {
}
#list used to keep track of all messageboxes (lists)
qList = []
#variable that assigns an ID to newly spawned thread, used to correspond to a messagebox 
tCount = 0


#function used to add a new message to all users' messageboxes
def addStringToQueue(ID, string):
    for x in qList:
        if x[0] != str(ID):
            x.append(string)
    return



#thread function, one is spawned per connected client
def chatRecThread(userDict, connectionSocket, tCount):
    wordCount = 0
    name = ""
    #obtains JOIN message
    message = connectionSocket.recv(1024).decode()
    message = message.splitlines()
    if message[1] == "JOIN":
        name = message[2]
        name = name[10:]
        if name in userDict:
            wordCount = userDict[name]
        else:
            userDict[name] = 0
    #Responds to JOIN message with welcome response, instructs user how to exit the chat
    responseMsg = "-Welcome " + name + "\n-Type \"\\leave\" to exit the chat"
    response = chatVersion + "\n" + "TEXT\n" + responseMsg
    connectionSocket.send(response.encode())
    addStringToQueue(tCount-1,"-Welcome " + name)
    connected = True
    
    #continually loops, sending messages if one is available and receiving messages when socket is readable
    while message[1] != "LEAVE":
        try:
            is_readable = [connectionSocket]
            is_writable = []
            is_error = []
            r, w, e = select.select(is_readable,is_writable,is_error, 1.0)
            if r:
                message = connectionSocket.recv(1024).decode()
                message = message.splitlines()
                if message[1] == "TEXT":
                    lengthParam = message[3].strip().split(" ")
                    wordCount += int(lengthParam[1])
                    userDict[name] = wordCount
                    string = ">" + name + ": " + message[4]
                    addStringToQueue(tCount-1,string)
            #checks messagebox for new outbound message, sends if a match is found
            for x in qList:
                if x[0] == str(tCount -1) and len(x) > 1:
                    message = chatVersion +"\n" + "TEXT\n" + x.pop(1)
                    connectionSocket.send(message.encode())
                    break
        except:
            connected = False
            break
    
    #sends farewell message with the number of words the user has typed across all sessions     
    responseMsg = "-Bye " + name + " " + str(wordCount)
    response = chatVersion + "\n" + "TEXT\n" + responseMsg
    if(connected):
        connectionSocket.send(response.encode())
        connectionSocket.close()
    addStringToQueue(tCount-1,responseMsg)
    
    #Clears the unneeded message box from the list of messageboxes
    for x in qList:
        if x[0] == str(tCount -1):
            qList.remove(x)
            break
    
    
    return

while True:
    connectionSocket, addr = serverSocket.accept()
    #creates a new messaage box associated with newly spawned thread
    qList.append(list(str(tCount)))
    tCount += 1
    Thread(target=chatRecThread, args=(userDict,connectionSocket,tCount)).start()
    

