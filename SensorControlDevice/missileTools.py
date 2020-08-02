import board
import busio
import adafruit_ina219
import adafruit_pca9685
import adafruit_bno055
import time
import sys

############################################################

print('Running missileTools initialization')

########################################################
#Define all variables#
############################################################
#instantiate all sensors#

i2c_bus = busio.I2C(board.SCL, board.SDA)
time.sleep(0.25)

ina219 = adafruit_ina219.INA219(i2c_bus, 0x41)
time.sleep(0.25)

pca = adafruit_pca9685.PCA9685(i2c_bus, address = 0x40)
time.sleep(0.25)
pca.frequency = 50

time.sleep(0.25)
bno055 = adafruit_bno055.BNO055(i2c_bus)
time.sleep(0.25)

### CONSTANTS ###
## FIN NUMBERING: Looking from behind the missle
## 0 = bottom, 1 = top, 2 = right, 3 = left

##Fine-tuning variables for each fin
servoTrim = [-16, 0, 0, -12]

##Offsets used to change angle of each fin
servoOffset = [ 90, 90, 90, 90]

#PCA9685 variables
##Servo constraint values, 0x1f40 = 8000, 07d0 = 2000
maxVal = 0x1f40
minVal = 0x07d0
midVal = int(((maxVal - minVal) / 2) + minVal)

#Misc. variables
ditherDelay = 0.1


print('Running missileTools board initialization')
#INA219 voltage/current sensor variables
shuntVoltage = 0.0
busVoltage = 0.0
current_mA = 0.0
loadVoltage = 0.0
power_mW = 0.0
#BNO055 variable
eulerAngle = (0,0,0)
#Send initial pwm signals(servo values)
for i in range(0,4):
    pca.channels[i].duty_cycle = midVal

###########################################################
#define all methods#

##Read INA219 (Current Sensor) and update variables
def readINA219():
    global shuntVoltage, busVoltage, current_mA, loadVoltage, power_mW, ina219
    shuntVoltage = ina219.shunt_voltage
    busVoltage = ina219.bus_voltage
    current_mA = ina219.current
    loadVoltage = 0.0
    power_mW = current_mA * shuntVoltage


##Read BNO055(IMU) and update fin angles
def readBNO055():
    global eulerAngle
    eulerAngle = bno055.euler
#    adaptFin(eulerAngle[0], eulerAngle[1], eulerAngle[2])


##map a given value from one range to another
##value == the value to change,  x == being current range, y == being desired range
def map(value, xmin, xmax, ymin, ymax):
    newValue = value / (xmax-xmin)
    newValue = (newValue * (ymax-ymin)) + ymin
    return int(newValue)

## contrains a value to be within a certain range
def constrain(value, min, max):
    if value > max:
        newValue = max
    elif value < min:
        newValue = min
    else:
        return int(value)
    return int(newValue)

##used in dither() Function
##each servo has its it's own "zero-point"
##this function chooses the right one
def chooseZero(servoChoice):
    global servoTrim
    return 90 + servoTrim[servoChoice]

##Dither - moves fin back and forth, functions more as a test of movement
def dither(servoChoice):
    global pca
    fwd = 95
    bwd = 85

    for i in range(0,10):
        pca.channels[servoChoice].duty_cycle = map(fwd, 0,180, minVal, maxVal)
        time.sleep(ditherDelay)
        pca.channels[servoChoice].duty_cycle = map(bwd, 0,180, minVal, maxVal)
        time.sleep(ditherDelay)

    pca.channels[servoChoice].duty_cycle = map( 90 + servoTrim[servoChoice], 0,180, minVal, maxVal)


## Adaptive motion
### This function uses the gyroscope to adjust the fin postion according to the
### missle orientation
def adaptFin():
    global pca, servoTrim, servoOffset, minVal, maxVal

    yaw = eulerAngle[0]
    pitch = eulerAngle[1]
    roll = eulerAngle[2]

    servoAngle = [0, 0, 0, 0]

    servoAngle[2] = constrain(map( (90 + -1*pitch + servoTrim[2]), 0,180, minVal, maxVal), minVal, maxVal)
    servoAngle[3] = constrain(map( (90 + pitch + servoTrim[3]), 0,180, minVal, maxVal), minVal, maxVal)

    if yaw > 180:
        servoAngle[0] = constrain(map( (90 + -1*(yaw - 360) + servoTrim[0]), 0,180, minVal, maxVal), minVal, maxVal)

        servoAngle[1] = constrain(map( (90 + (yaw - 360) + servoTrim[1]), 0,180, minVal, maxVal), minVal, maxVal)

    else:
        servoAngle[0] = constrain(map( (90 + -1*yaw + servoTrim[0]), 0,180, minVal, maxVal), minVal, maxVal)
        servoAngle[1] = constrain(map( (90 + yaw + servoTrim[1]), 0,180, minVal, maxVal), minVal, maxVal)

    # set the servo angles
    for i in range(0,4):
        pca.channels[i].duty_cycle = servoAngle[i]



# This function sets the servo angle
def setServoAngle(message):
    global servoOffset, bno055
    angle = int(message[1:])
    servoChoice = int(message[0])

    print("Servo Choice: ", servoChoice)
    print("Angle: ", angle)

    if servoChoice > 3 or servoChoice < 0:
        return

    if angle == 200:
        dither(servoChoice)
        return
    elif angle == 210:
        #reset Gyro
        bno055 = adafruit_bno055.BNO055(i2c_bus)
        time.sleep(1)
        return
    elif angle == 220:
        print("Terminating Connection")
        sys.exit()
    if angle > 180 or angle < 0:
        return

    pca.channels[servoChoice].duty_cycle = constrain( map( servoTrim[servoChoice] + angle, 0, 180, minVal, maxVal), minVal, maxVal)
