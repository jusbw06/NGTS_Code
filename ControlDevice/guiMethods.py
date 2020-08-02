import cfg
import commTools as cT
import sys
import socket
import os

phi = None
theta = None
psi = None
pwr = None
amp = None

seeker_mode = None
gyro_mode = None
message_board = None

##################  Methods   ############################
        
def shutdown():
    cT.sendData('#SHUTDOWN', cfg.SERVO_SOCK)
    os.system("shutdown now")
        
def closeProgram():
    cT.sendData('#EXIT', cfg.SERVO_SOCK)
    sys.exit()

#######################  Servo Control Methods   ####################

def turnServo(fin, degrees):
    string = '#' + str(fin) + str( int(degrees) + 90 )
    cT.sendData(string, cfg.SERVO_SOCK)
    
def resetYaw():
    cT.sendData('#1210', cfg.SERVO_SOCK)    

def seekerModeOn():
    cT.sendData('#SEEKON', cfg.SERVO_SOCK)    
def seekerModeOff():
    cT.sendData('#SEEKOFF', cfg.SERVO_SOCK)
def gyroModeOn():
    cT.sendData('#GYROON', cfg.SERVO_SOCK)    
def gyroModeOff():
    cT.sendData('#GYROOFF', cfg.SERVO_SOCK)

def dither(fin):
    cT.sendData( '#' + str(fin) + '200', cfg.SERVO_SOCK )    
    
def updateLiterals():
    items = cT.receiveData(cfg.SERVO_SOCK)
    for item in items:
        if item == "":
            pass
        else:
            if item[0] == 'I':
                amp.value= "A=" + item[1:]
            elif item[0] == 'P':
                pwr.value= "mW=" + item[1:]
            elif item[0] == 'X':
                phi.value= "phi=" + item[1:]
            elif item[0] == 'Y':
                theta.value= "theta=" + item[1:]
            elif item[0] == 'Z':
                psi.value= "psi=" + item[1:]
            elif item == 'GYROON':
                gyro_mode.value = "Gyro Mode: ON"
            elif item == 'GYROOFF':
                gyro_mode.value = "Gyro Mode: OFF"
            else:
                message_board.value = "Servo Message: " + item
                
                
def updateJetsonLiterals():
    items = cT.receiveData(cfg.JETSON_SOCK)
    for item in items:
        if item == "":
            pass
        else:
            if item == 'SEEKON':
                seeker_mode.value = "Seeker Mode: ON"
            elif item == 'SEEKOFF':
                seeker_mode.value = "Seeker Mode: OFF"
            else:
                message_board.value = "Jetson Message: " + item
