#!/usr/bin/python3

import socket
from guizero import App, Box, Text, Slider, PushButton
import cfg
import guiMethods as gM



if __name__ == '__main__':

    # initialization
    # Create Server

    s = socket.socket()
    print("Socket successfully created")
    s.bind((cfg.GUI_IP,cfg.PORT_NUM))
    s.listen(2)
    print("socket is listening")
    s.settimeout(None)

    connections = 0
    while connections < 2:
        sock, addr = s.accept()
        if addr[0] == cfg.JETSON_IP:
            cfg.JETSON_SOCK = sock
            sock.settimeout(cfg.JETSON_TIMEOUT)
            print('Jetson is connected')
            connections += 1
        elif addr[0] == cfg.SERVO_IP:    
            cfg.SERVO_SOCK = sock
            sock.settimeout(cfg.SERVO_TIMEOUT)
            print('Servo is connected')
            connections += 1
        else:
            sock.close()

################# CREATE APPLICATION ################# 

    # Create the App
    app = App(title= "NGTS Missile", layout="auto")
    app1 = Box(app,layout="grid")

    # Wrapper Boxes
    title_box = Box(app1, layout="auto", grid=[1,0,2,1])
    slider_box = Box(app1, layout="grid", grid=[0,1])
    parameter_box = Box(app1, layout="grid", grid=[1,1])
    notification_box = Box(app1, layout="grid", grid=[0,2,2,1])

    # Title Box -- Top
    title_text = Text(title_box, "NGTS Missile Test", align="top")

    # Slider Box -- Left
    text_left = Text(slider_box, "left", grid=[0,2])
    slider_left = Slider(slider_box,  command=lambda x:gM.turnServo(cfg.SERVO_LEFT, x), start=-90, end=90, grid=[0,3])
    dither_left = PushButton(slider_box, text="dither",command=lambda:gM.dither(cfg.SERVO_LEFT), grid=[0,4])
    
    text_top = Text(slider_box, "top", grid=[1,0])
    slider_top = Slider(slider_box,  command=lambda x:gM.turnServo(cfg.SERVO_TOP, x), start=-90, end=90, grid=[1,1])
    dither_top = PushButton(slider_box, text="dither", command=lambda:gM.dither(cfg.SERVO_TOP),grid=[1,2])
    
    text_bottom = Text(slider_box, "bottom", grid=[1,5])
    slider_bottom = Slider(slider_box,  command=lambda x:gM.turnServo(cfg.SERVO_BOTTOM,x), start=-90, end=90, grid=[1,6])
    dither_bottom = PushButton(slider_box, text="dither",command=lambda:gM.dither(cfg.SERVO_BOTTOM), grid=[1,7])
    
    text_right = Text(slider_box, "right", grid=[2,2])
    slider_right = Slider(slider_box,  command=lambda x:gM.turnServo(cfg.SERVO_RIGHT,x), start=-90, end=90, grid=[2,3])
    dither_right = PushButton(slider_box, text="dither", command=lambda:gM.dither(cfg.SERVO_RIGHT),grid=[2,4])


    # Parameter & Button Box -- Right
    text_phi = Text(parameter_box, "phi=", grid=[0,0])
    text_phi.value="phi=0" # <--- changes displayed value
    gM.phi = text_phi
    text_theta = Text(parameter_box, "theta=", grid=[0,1])
    text_theta.value="theta=0"
    gM.theta = text_theta
    text_psi = Text(parameter_box, "psi=", grid=[0,2])
    text_psi.value="psi=0"
    gM.psi = text_psi
    text_power = Text(parameter_box, "mW=", grid=[0,3])
    text_power.value="mW=0"
    gM.pwr = text_power
    text_amp = Text(parameter_box, "A=", grid=[0,4])
    text_amp.value="A=0"
    gM.amp = text_amp
    
    toggle_num_reset = PushButton(parameter_box, text="RESET Yaw", command=gM.resetYaw, grid=[0,5])
    toggle_seeker_on = PushButton(parameter_box, text="Seeker Mode On", command=gM.seekerModeOn, grid=[0,6])
    toggle_seeker_off = PushButton(parameter_box, text="Seeker Mode Off", command=gM.seekerModeOff, grid=[1,6])
    toggle_gyro_on = PushButton(parameter_box, text="Gyro Mode On", command=gM.gyroModeOn, grid=[0,7])
    toggle_gyro_off = PushButton(parameter_box, text="Gyro Mode Off", command=gM.gyroModeOff, grid=[1,7])
    toggle_exit = PushButton(parameter_box, text="Exit", command=gM.closeProgram, grid=[0,8])
    toggle_shutdown = PushButton(parameter_box, text="Exit & Shutdown", command=gM.shutdown, grid=[1,8])


    # Notification Box -- Bottom
    text_seeker_mode = Text(notification_box, text="Seeker Mode: OFF", grid=[0,0])
    gM.seeker_mode = text_seeker_mode
    text_gyro_mode = Text(notification_box, text="Gyro Mode: OFF", grid=[0,1])
    gM.gyro_mode = text_gyro_mode    
    text_message_board = Text(notification_box, text="Message: N/A", grid=[0,2])
    gM.message_board = text_message_board


    # Display
    app.repeat(10, gM.updateLiterals)    
    app.repeat(100, gM.updateJetsonLiterals)
    app.tk.attributes("-fullscreen",True)
    app.display()

################# CREATE APPLICATION END ################# 


