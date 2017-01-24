#!/usr/bin/env python
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for running a motor a target speed (specified in Degrees Per Second) set by the encoder of another motor.
# 
# Hardware: Connect EV3 or NXT motors to the BrickPi3 motor ports A and D. Make sure that the BrickPi3 is running on a 9v power supply.
#
# Results:  When you run this program, motor A speed will be controlled by the position of motor D. Manually rotate motor D, and motor A's speed will change.

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

try:
    BP.offset_motor_encoder(BP.PORT_A, BP.get_motor_encoder(BP.PORT_A)[0]) # reset encoder A
    BP.offset_motor_encoder(BP.PORT_D, BP.get_motor_encoder(BP.PORT_D)[0]) # reset encoder D
    BP.set_motor_speed(BP.PORT_D, -128)                                    # float motor D
    while True:
        # BP.get_motor_encoder function return a list of 2 values
        #     The first item in the list is the value (what we want to use).
        #     The second item in the list is the error value (should be equal to BP.SUCCESS if the value was read successfully)
        target = BP.get_motor_encoder(BP.PORT_D)[0]     # read motor D's position
        
        BP.set_motor_dps(BP.PORT_A, target)             # set the target speed for motor A in Degrees Per Second
        
        print("Target Degrees Per Second: %d" % target)
        
        time.sleep(0.02)

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
