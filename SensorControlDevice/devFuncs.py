import cfg
import missileTools as mT
import sys
import os

def recUpdateState():
    messages = receiveData( cfg.GUI_SOCK )
    if messages != None:
        for item in messages:
            if item == "":
                continue
            elif item == 'SEEKON':
                cfg.SEEKER_MODE = True
                sendData("#SEEKON",cfg.JETSON_SOCK)
            elif item == 'SEEKOFF':
                cfg.SEEKER_MODE = False
                sendData("#SEEKOFF",cfg.JETSON_SOCK)
            elif item == 'GYROON':
                cfg.GYRO_MODE = True
                sendData("#GYROON", cfg.GUI_SOCK)
            elif item == 'GYROOFF':
                cfg.GYRO_MODE = False
                sendData('#GYROOFF', cfg.GUI_SOCK)
            elif item == 'EXIT':
                sendData("#EXIT", cfg.JETSON_SOCK)
                sys.exit()
            elif item == 'SHUTDOWN':
                sendData("#SHUTDOWN", cfg.JETSON_SOCK)
                os.system("shutdown now")
            elif cfg.SEEKER_MODE == False and cfg.GYRO_MODE == False:
                mT.setServoAngle(item)

def sendStateLiterals():
    mT.current_mA = mT.current_mA / 1000
    sendData("#I" + str('%.4f'%mT.current_mA), cfg.GUI_SOCK)
    sendData("#P" + str('%.4f'%mT.power_mW), cfg.GUI_SOCK)
    sendData("#X" + str('%.4f'%mT.eulerAngle[0]), cfg.GUI_SOCK)
    sendData("#Y" + str('%.4f'%mT.eulerAngle[1]), cfg.GUI_SOCK)
    sendData("#Z" + str('%.4f'%mT.eulerAngle[2]), cfg.GUI_SOCK)

def toJetson():
    messages = receiveData( cfg.JETSON_SOCK )
    if messages != None:
        for item in messages:
            if item == "":
                continue
            mT.setServoAngle(item)

## receive data over wifi
def receiveData(fd):
    try:
        messageReceived = fd.recv(1024)
    except:
        return ""
    messageReceived = bytes.decode(messageReceived)
    messageReceived = messageReceived.split("#")
    return messageReceived


## send data over wifi
def sendData(messageToEncode, fd):
    messageToSend = messageToEncode.encode('utf-8')
    fd.sendall(messageToSend)
