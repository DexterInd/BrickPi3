#!/usr/bin/env python3
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2026 Modular Robotics Inc
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for a line following robot using the BrickPi3
#
# Hardware:
#     Connect Line Follower sensor to the BrickPi3 Grove I2C port
#     Connect left motor to BrickPi3 motor port B
#     Connect right motor to BrickPi3 motor port C

import sys      # import sys for sys.exit()
import time     # import the time library for loop delay timing
import brickpi3 # import the BrickPi3 drivers
from di_sensors import easy_line_follower # import the Line Follower drivers

bp = brickpi3.BrickPi3()                   # bp will be the BrickPi3 object
lf = easy_line_follower.EasyLineFollower() # lf will be the EasyLineFollower object

PORT_MOTOR_LEFT  = bp.PORT_B # specify the motor ports
PORT_MOTOR_RIGHT = bp.PORT_C #          ''

DRIVE_BASE_SPEED = 300       # the drive motor speed, in Degrees Per Second

LoopTime = 0
def LoopDelay(hz):
    global LoopTime
    CurrentTime = time.time()
    SleepTime = LoopTime - CurrentTime
    if SleepTime > 0: # delay if necessary
        time.sleep(LoopTime - CurrentTime)
    else: # Attempting to loop faster than possible. Don't get behind.
        LoopTime = CurrentTime
    LoopTime += (1 / hz)

def SafeExit():
    ''' This method is called to stop the BrickPi3 and perform a clean program exit '''
    bp.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
    sys.exit()

try:
    print("BrickPi3 Tracked Line Follower.")
    print("")

    # make sure voltage is high enough
    if bp.get_voltage_battery() < 7.2:
        print("Battery voltage below 7.2v. Too low to run motors reliably. Exiting.")
        SafeExit()

    # reset the BrickPi3 configuration and encoders
    bp.reset_all()
    bp.offset_motor_encoder(PORT_MOTOR_LEFT, bp.get_motor_encoder(PORT_MOTOR_LEFT))
    bp.offset_motor_encoder(PORT_MOTOR_RIGHT, bp.get_motor_encoder(PORT_MOTOR_RIGHT))

    while True:
        LoopDelay(100) # loop at the specified frequency

        LineFollowerState = lf.read("weighted-avg")
        if LineFollowerState[1] != 0:
            bp.set_motor_dps(PORT_MOTOR_LEFT, 0)
            bp.set_motor_dps(PORT_MOTOR_RIGHT, 0)
        else:
            Error = -(LineFollowerState[0] - 0.5) * 2
            if Error > 1:
                Error = 1
            elif Error < -1:
                Error = -1

            Correction = Error * 3

            bp.set_motor_dps(PORT_MOTOR_LEFT, (DRIVE_BASE_SPEED - (DRIVE_BASE_SPEED * Correction)))
            bp.set_motor_dps(PORT_MOTOR_RIGHT, (DRIVE_BASE_SPEED + (DRIVE_BASE_SPEED * Correction)))

except KeyboardInterrupt:
    SafeExit()
