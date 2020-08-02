#!/usr/bin/python3

import socket
import cfg
import missileTools as mT
import devFuncs as dev
import time

if __name__ == "__main__":

    # create connection
    connected = False
    sock = socket.socket()
    sock.settimeout(None)
    while not connected:
        try:
            sock.connect((cfg.JETSON_IP, cfg.PORT_NUM))
            cfg.JETSON_SOCK = sock
            sock.settimeout(cfg.JETSON_TIMEOUT)
            print('connected to Jetson')
            connected = True
        except:
            time.sleep(1)
    
    connected = False
    sock = socket.socket()
    sock.settimeout(None)
    while not connected:
        try:
            sock.connect((cfg.GUI_IP, cfg.PORT_NUM))
            cfg.GUI_SOCK = sock
            sock.settimeout(cfg.GUI_TIMEOUT)
            print('connected to GUI')
            connected = True
        except:
            time.sleep(1)


    # both connections established
    # start
    while True:

###############################

        mT.readINA219()
        mT.readBNO055()

###############################

        # send panel variables
        dev.sendStateLiterals()
        # rec information from GUI & update servos
        dev.recUpdateState()

        # receive data from Jetson
        if cfg.SEEKER_MODE:
            dev.toJetson()

        # update servos via gyro
        if cfg.GYRO_MODE:
            mT.adaptFin()

################################



