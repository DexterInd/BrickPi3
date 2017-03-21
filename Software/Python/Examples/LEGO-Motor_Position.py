#!/usr/bin/env python
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for running a motor to a target position set by the encoder of another motor.
# 
# Hardware: Connect EV3 or NXT motors to the BrickPi3 motor ports A and D. Make sure that the BrickPi3 is running on a 9v power supply.
#
# Results:  When you run this program, motor A will run to match the position of motor D. Manually rotate motor D, and motor A will follow.

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

try:
    BP.offset_motor_encoder(BP.PORT_A, BP.get_motor_encoder(BP.PORT_A)[0]) # reset encoder A
    BP.offset_motor_encoder(BP.PORT_D, BP.get_motor_encoder(BP.PORT_D)[0]) # reset encoder D
    BP.set_motor_power(BP.PORT_D, BP.MOTOR_FLOAT)                          # float motor D
    #BP.set_motor_limits(BP.PORT_A, 25)                                     # optionally set a power limit
    while True:
        # Each of the following BP.get_motor_encoder functions return a list of 2 values
        #     The first item in the list is the value (what we want to display).
        #     The second item in the list is the error value (should be equal to BP.SUCCESS if the value was read successfully)
        target = BP.get_motor_encoder(BP.PORT_D)[0] # read motor D's position
        
        BP.set_motor_position(BP.PORT_A, target)    # set motor A's target position to the current position of motor D
        
        print("Motor A target: %6d  Motor A position: %6d" % (target, BP.get_motor_encoder(BP.PORT_A)[0]))
        
        time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
