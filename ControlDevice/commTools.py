import cfg
import socket

##receive data over wifi
def receiveData(fd):
    try:
        messageReceived = fd.recv(1024)
    except:
        return ""
    messageReceived = bytes.decode(messageReceived)
    messageReceived = messageReceived.split("#")
    return messageReceived


##send data over wifi
def sendData(messageToEncode, sock):
    messageToSend = messageToEncode.encode('utf-8')
    sock.sendall(messageToSend)


