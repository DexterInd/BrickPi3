#!/usr/bin/env python
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for running all motors while a touch sensor connected to PORT_1 of the BrickPi3 is being pressed.
# 
# Hardware: Connect EV3 or NXT motor(s) to any of the BrickPi3 motor ports. Make sure that the BrickPi3 is running on a 9v power supply.
#
# Results:  When you run this program, the motor(s) speed will ramp up and down while the touch sensor is pressed. The position for each motor will be printed.

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.TOUCH) # Configure for a touch sensor. If an EV3 touch sensor is connected, it will be configured for EV3 touch, otherwise it'll configured for NXT touch.

try:
    print("Press touch sensor on port 1 to run motors")
    while not BP.get_sensor(BP.PORT_1)[0]: # Wait until the touch sensor is pressed
        time.sleep(0.02)
    
    speed = 0
    adder = 1
    while True:
        # BP.get_sensor retrieves a sensor value.
        # BP.PORT_1 specifies that we are looking for the value of sensor port 1.
        # BP.get_sensor returns a list of two values.
        #     The first item in the list is the sensor value (what we want to check).
        #     The second item in the list is the error value (should be equal to BP.SUCCESS if the value was read successfully)
        if BP.get_sensor(BP.PORT_1)[0]:       # if the touch sensor is pressed
            if speed <= -100 or speed >= 100: # if speed reached 100, start ramping down. If speed reached -100, start ramping up.
                adder = -adder
            speed += adder
        else:                                 # else the touch sensor is not pressed, so set the speed to 0
            speed = 0
            adder = 1
        
        # Set the motor speed for all four motors
        BP.set_motor_power(BP.PORT_A, speed)
        BP.set_motor_power(BP.PORT_B, speed)
        BP.set_motor_power(BP.PORT_C, speed)
        BP.set_motor_power(BP.PORT_D, speed)
        
        # Each of the following BP.get_motor_encoder functions return a list of 2 values
        #     The first item in the list is the value (what we want to display).
        #     The second item in the list is the error value (should be equal to BP.SUCCESS if the value was read successfully)
        print("Encoder A: %6d  B: %6d  C: %6d  D: %6d" % (BP.get_motor_encoder(BP.PORT_A)[0], BP.get_motor_encoder(BP.PORT_B)[0], BP.get_motor_encoder(BP.PORT_C)[0], BP.get_motor_encoder(BP.PORT_D)[0]))
        
        time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
