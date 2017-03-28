#!/usr/bin/env python
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for a balanging robot using the BrickPi3
# 
# Hardware:
#     Connect an EV3 infrared sensor to BrickPi3 sensor port 1.
#     Connect a gyro sensor to BrickPi3 sensor port 4.
#     Connect the left motor to BrickPi3 motor port A.
#     Connect the right motor to BrickPi3 motor port D.
#     Set EV3 infrared remote to channel 1.
# 
# Results:  When you run this program, follow the instruction printed in the terminal.

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers
import sys      # import sys for sys.exit()

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

# define which ports the sensors and motors are connected to.
PORT_SENSOR_IR   = BP.PORT_1
PORT_SENSOR_GYRO = BP.PORT_4
PORT_MOTOR_RIGHT = BP.PORT_A
PORT_MOTOR_LEFT  = BP.PORT_D

# define constants for the Lego EV3 gyro and HiTechnic gyro
GYRO_EV3       = 1
GYRO_HiTechnic = 2

GYRO_TYPE = GYRO_EV3   # this can be set to GYRO_EV3 (for the Lego EV3 gyro sensor) or GYRO_HiTechnic (for the HiTechnic gyro sensor)

WHEEL_DIAMETER = 43.2  # Lego wheel diameter in mm. The size is moulded onto the sidewall of the Lego tires. The tires included with the EV3 retail set are 43.2mm, and the tires included with the EV3 education set are 56mm

LOOP_SPEED = 120       # how fast to run the balance loop in Hz. Slower is less CPU intensive, but faster helps the balance bot to work better. Realistically anything over 120 doesn't make a difference.

DRIVE_SPEED = 350      # how fast to drive when being controlled by the remote
STEER_SPEED = 250      # how fast to steer when being controlled by the remote

KCORRECTTIME = 0.001   # a constant used to correct the delay to try to maintain a perfect loop speed (defined by LOOP_SPEED)

if GYRO_TYPE == GYRO_EV3:
    KGYROSPEEDCORRECT = 0.01 # a constant used to correct the gyro speed readings
elif GYRO_TYPE == GYRO_HiTechnic:
    KGYROSPEEDCORRECT = 0.25 # a constant used to correct the gyro speed readings
else:
    print("GYRO_TYPE must be GYRO_EV3 or GYRO_HiTechnic. Exiting.")
    SafeExit()

KGYROANGLECORRECT = 0.25 # a constant used to correct/center the gyro accumulated angle so that gyro integral drift works itself out faster than it can accumulate.

# constants used to define how agressively the robot should respond to:
KGYROANGLE = 14    # sudden changes in angle
KGYROSPEED = 1.2   # overall angle
KPOS       = 0.07  # deviation from the target position
KSPEED     = 0.1   # the actual speed of the motor
KDRIVE     = -0.02 # the drive speed target (helps the robot start/stop driving)
KSTEER     = 0.25  # an error in the steering of the robot

TIME_FALL_LIMIT = 2 # if the motors have been running at full power for 2 seconds, assume that the robot fell.

WHEEL_RATIO = (WHEEL_DIAMETER / 56) # tuned for 56mm wheels
LOOP_TIME = (1 / LOOP_SPEED)        # how many seconds each loop should take (at 100 Hz, this should be 0.01)

# call this function to turn off the motors and exit safely.
def SafeExit():
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
    sys.exit()

try:
    print("BrickPi3 BalanceBot.")
    
    # make sure voltage is high enough
    if BP.get_voltage_battery() < 7:
        print("Battery voltage below 7v, too low to run motors reliably. Exiting.")
        SafeExit()
    
    # un-configure the gyro sensor, and configure the IR sensor in remote mode, and wait for it to be configured.
    print("Configuring Infrared Receiver...")
    
    BP.set_sensor_type(PORT_SENSOR_GYRO, BP.SENSOR_TYPE.NONE)
    BP.set_sensor_type(PORT_SENSOR_IR, BP.SENSOR_TYPE.EV3_INFRARED_REMOTE)
    time.sleep(0.25)
    Continue = False
    while not Continue:
        try:
            BP.get_sensor(PORT_SENSOR_IR)
            Continue = True
        except brickpi3.SensorError:
            pass
        time.sleep(0.1)
    
    # IR receiver is configured. Wait to continue until Red Up is pressed.
    print("Lay robot down so that it is perfectly still, then press Red Up on the remote.")
    while not BP.get_sensor(PORT_SENSOR_IR)[0][0]:
        time.sleep(0.1)
    
    # configure gyro sensor in Degrees Per Second mode, and wait for it to be configured.
    print("Configuring Gyro Sensor... Keep robot still.")
    
    gOffset = 0
    
    if GYRO_TYPE == GYRO_EV3:
        BP.set_sensor_type(PORT_SENSOR_GYRO, BP.SENSOR_TYPE.EV3_GYRO_DPS)
        Continue = False
        while not Continue:
            try:
                gOffset = BP.get_sensor(PORT_SENSOR_GYRO)
                Continue = True
            except brickpi3.SensorError:
                pass
            time.sleep(0.1)
    elif GYRO_TYPE == GYRO_HiTechnic:
        BP.set_sensor_type(PORT_SENSOR_GYRO, BP.SENSOR_TYPE.CUSTOM, [(BP.SENSOR_CUSTOM.PIN1_ADC)])#BP.SENSOR_TYPE.EV3_GYRO_DPS)
        Continue = False
        while not Continue:
            try:
                gOffset = BP.get_sensor(PORT_SENSOR_GYRO)[0] / 4
                Continue = True
            except brickpi3.SensorError:
                pass
            time.sleep(0.1)
    
    print("Stand robot up, then press Blue Up on the remote.")
    while not BP.get_sensor(PORT_SENSOR_IR)[0][2]:
        time.sleep(0.1)
    
    print("Release Blue Up on the remote.")
    
    while BP.get_sensor(PORT_SENSOR_IR)[0][2]:
        time.sleep(0.1)
    
    if BP.get_sensor(PORT_SENSOR_IR)[0][0]:
        print("Release Red Up on the remote.")
        while BP.get_sensor(PORT_SENSOR_IR)[0][0]:
            time.sleep(0.1)
    
    # reset the encoders
    BP.offset_motor_encoder(PORT_MOTOR_LEFT, BP.get_motor_encoder(PORT_MOTOR_LEFT))
    BP.offset_motor_encoder(PORT_MOTOR_RIGHT, BP.get_motor_encoder(PORT_MOTOR_RIGHT))
    
    # get the current time in ms
    CurrentTick = int(round(time.time() * 1000))
    
    tMotorPosOK = CurrentTick
    #tCalcStart = CurrentTick - LOOP_TIME
    NextBalanceTime = CurrentTick
    
    gyroAngle = 0
    mrcSum = 0
    motorPos = 0
    mrcDelta = 0
    mrcDeltaP1 = 0
    mrcDeltaP2 = 0
    mrcDeltaP3 = 0
    motorDiffTarget = 0
    
    LastTime = time.time() - LOOP_TIME
    TimeOffset = 0
    tInterval = LOOP_TIME
    
    print("Balancing, so let go of the robot.")
    print("Use Red and Blue Up and Down to drive the robot.")
    
    while True:
        try:
            # loop at exactly the speed specified by LOOP_SPEED, and set tInterval to the actual loop time
            CurrentTime = time.time()
            TimeOffset += ((tInterval - LOOP_TIME) * KCORRECTTIME) # use this to adjust for any overheads, so that it tries to loop at exactly the speed specified by LOOP_SPEED
            DelayTime = (LOOP_TIME - (CurrentTime - LastTime)) - TimeOffset
            if DelayTime > 0:
                time.sleep(DelayTime)
            CurrentTime = time.time()
            tInterval = (CurrentTime - LastTime)
            LastTime = CurrentTime
            #print(tInterval, TimeOffset)
            
            motorControlDrive = 0
            motorControlSteer = 0
            
            Buttons = BP.get_sensor(PORT_SENSOR_IR)[0]
            
            if Buttons[0]:
                motorControlDrive -= DRIVE_SPEED
                motorControlSteer -= STEER_SPEED
            elif Buttons[1]:
                motorControlDrive += DRIVE_SPEED
                motorControlSteer += STEER_SPEED
            
            if Buttons[2]:
                motorControlDrive -= DRIVE_SPEED
                motorControlSteer += STEER_SPEED
            elif Buttons[3]:
                motorControlDrive += DRIVE_SPEED
                motorControlSteer -= STEER_SPEED
            
            if GYRO_TYPE == GYRO_EV3:
                gyroSpeed = BP.get_sensor(PORT_SENSOR_GYRO) - gOffset
            elif GYRO_TYPE == GYRO_HiTechnic:
                gyroSpeed = BP.get_sensor(PORT_SENSOR_GYRO)[0] / 4 - gOffset
            
            gOffset += (gyroSpeed * KGYROSPEEDCORRECT * tInterval)
            
            gyroAngle += gyroSpeed * tInterval
            gyroAngle -= (gyroAngle * KGYROANGLECORRECT * tInterval)
            
            mrcLeft = BP.get_motor_encoder(PORT_MOTOR_LEFT)
            mrcRight = BP.get_motor_encoder(PORT_MOTOR_RIGHT)
            mrcSumPrev = mrcSum
            mrcSum = mrcLeft + mrcRight
            motorDiff = mrcLeft - mrcRight
            mrcDelta = mrcSum - mrcSumPrev
            motorPos += mrcDelta
            motorSpeed = mrcDelta / tInterval
            
            motorPos -= motorControlDrive * tInterval
            
            power = ((KGYROSPEED * gyroSpeed +                # (Deg/Sec from Gyro sensor
                     KGYROANGLE * gyroAngle) / WHEEL_RATIO +  # Deg from integral of gyro) / wheel ratio (tuned for 56mm wheels)
                     KPOS       * motorPos +                  # From MotorRotaionCount of both motors
                     KDRIVE     * motorControlDrive +         # To improve start/stop performance
                     KSPEED     * motorSpeed)                 # Motor speed in Deg/Sec
            
            if abs(power) < 100:
                tMotorPosOK = CurrentTime
            
            motorDiffTarget += motorControlSteer * tInterval
            powerSteer = KSTEER * (motorDiffTarget - motorDiff)
            powerLeft = power + powerSteer
            powerRight = power - powerSteer
            
            if powerLeft  >  100:
                powerLeft  =  100
            if powerLeft  < -100:
                powerLeft  = -100
            if powerRight >  100:
                powerRight =  100
            if powerRight < -100:
                powerRight = -100
            
            BP.set_motor_power(PORT_MOTOR_LEFT , powerLeft)
            BP.set_motor_power(PORT_MOTOR_RIGHT, powerRight)
            
            if (CurrentTime - tMotorPosOK) > TIME_FALL_LIMIT:
                print("Oh no! Robot fell. Exiting.")
                SafeExit()
            
        except brickpi3.SensorError as error:
            print(error)
        except IOError as error:
            print(error)
    
except KeyboardInterrupt:
    SafeExit()
