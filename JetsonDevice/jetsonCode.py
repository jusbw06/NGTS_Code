#!/usr/bin/python

import cfg
import socket
import time
import sys
import os


##send data over wifi
def sendData(messageToEncode, sock):
    messageToSend = messageToEncode.encode('utf-8')
    sock.sendall(messageToSend)

def processData( message ):
    for item in message:
        if item == "":
            continue
        elif item == 'SEEKON':
            cfg.SEEKER_MODE = True
            sendData("#SEEKON",cfg.GUI_SOCK)
        elif item == 'SEEKOFF':
            cfg.SEEKER_MODE = False
            sendData("#SEEKOFF",cfg.GUI_SOCK)
        elif item == 'EXIT':
            sys.exit()
        elif item == 'SHUTDOWN':
            os.system("shutdown now")


## ##
def recProcData(sock):
    messages = receiveData( sock )
    if messages != None:
        processData( messages )

def recUpdateState():
    recProcData(cfg.SERVO_SOCK)


##receive data over wifi
def receiveData(sock):
    try:
        messageReceived = sock.recv(1024)
    except:
        return ""
    messageReceived = bytes.decode(messageReceived)
    messageReceived = messageReceived.split("#")
    return messageReceived

# This method uses an alpha filter to dampen out the jerky motion associated with the object detection network
# It send the data to the servoPi in order to tell it what angle to turn the fins
def sendFinData(fins, angle):
    global servoDefaults
    for i in range(0,2):
        if i == 0:
            servoPrev[fins[i]] = 0.8 * ( angle + 90 )+ 0.2 * servoPrev[fins[i]]
        else:
            servoPrev[fins[i]] = 0.8 * ( angle + 90 ) * -1 + 0.2 * servoPrev[fins[i]]

        data  =  '#{0:1d}{1:3d}'.format(fins[i], ( int(servoPrev[fins[i]]) )  )
        print(data)
        try:
            sendData( data , cfg.SERVO_SOCK)
        except:
            return



import jetson.inference
import jetson.utils

import argparse

def map_coords(x_coor, y_coor):

    h = 720/2
    w = 1280/2

    x_rat = x_coor/w
    y_rat = y_coor/h

    new_angle_w = x_rat * 90
    new_angle_h = y_rat * 90

    sendFinData( (cfg.SERVO_TOP, cfg.SERVO_BOTTOM) , new_angle_w )
    sendFinData( (cfg.SERVO_LEFT, cfg.SERVO_RIGHT) , new_angle_h )


camera = None
net = None

def trackingAlgorithmInit():
    global camera, net
    # parse the command line
    parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", 
                               formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.detectNet.Usage())

    parser.add_argument("--network", type=str, default="coco-bottle", help="pre-trained model to load, see below for options")
    parser.add_argument("--threshold", type=float, default=0.5, help="minimum detection threshold to use")
    parser.add_argument("--camera", type=str, default="0", help="index of the MIPI CSI camera to use (NULL for CSI camera 0)\nor for VL42 cameras the /dev/video node to use.\nby default, MIPI CSI camera 0 will be used.")
    parser.add_argument("--width", type=int, default=1280, help="desired width of camera stream (default is 1280 pixels)")
    parser.add_argument("--height", type=int, default=720, help="desired height of camera stream (default is 720 pixels)")

    opt, argv = parser.parse_known_args()

    # load the object detection network
    net = jetson.inference.detectNet(opt.network, argv, opt.threshold)

    # create the camera
    camera = jetson.utils.gstCamera(opt.width, opt.height, opt.camera)

def trackingAlgorithm():

    display_height = 720
    display_width = 1280

    # process frames until user exits
    while cfg.SEEKER_MODE == True:

        # capture the image
        img, width, height = camera.CaptureRGBA()

        # detect objects in the image (with overlay)
        detections = net.Detect(img, width, height)

        # print the detections
        print("detected {:d} objects in image".format(len(detections)))

        for detection in detections:
            new_x = (detection.Center[0] - display_width/2)
            new_y = (detection.Center[1] - display_height/2)*-1
            print(detection)
            print('x: ' + str(new_x))
            print('y: ' + str(new_y))
            map_coords(new_x, new_y)

        # synchronize with the GPU
        if len(detections) > 0:
            jetson.utils.cudaDeviceSynchronize()

        # print out performance info
        net.PrintProfilerTimes()

        # update commands
        recUpdateState()


servoPrev = None
if __name__ == '__main__':
    global servoPrev
    # initialization

    # create connection to GUI
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

    print('waiting for servo')
    # Server listen for Connection from Servo
    s = socket.socket()
    s.settimeout(None)
    print('Socket Successfully Created')
    s.bind((cfg.JETSON_IP, cfg.PORT_NUM))
    print('Socket Successfully Binded')
    s.listen(1)
    print('Socket is Listening')
    sock, addr = s.accept()
    cfg.SERVO_SOCK = sock
    sock.settimeout(cfg.SERVO_TIMEOUT)
    print('received connection from servo')

    trackingAlgorithmInit()

    while True:

        # Upon Connection
        recUpdateState()


        if cfg.SEEKER_MODE == True:
            servoPrev = [90, 90, 90, 90]
            # run tracking algorithm
            trackingAlgorithm()

            # IR LASER POINTER
            # OTHER OPTION
