#!/usr/bin/env python3
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2026 Modular Robotics Inc
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for reading the encoders of motors connected to the BrickPi3.
#
# Hardware: Connect EV3 or NXT motor(s) to any of the BrickPi3 motor ports.
#
# Results:  When you run this program, you should see the encoder value for each motor. By manually rotating a motor, the count should change by 1 for every degree of rotation.

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

print("USER INSTRUCTIONS:")
print("Connect EV3 or NXT motors to any of the BrickPi3 motor ports (A, B, C, D).")
print("This program will continuously display encoder values from all motor ports.")
print("Manually rotate the motors to see encoder values change.")
print("Each degree of rotation should change the count by 1.")
input("Press Enter to continue...")

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

try:
    while True:
        # The following BP.get_motor_encoder function returns the encoder value
        try:
            print(f"Encoder A: {BP.get_motor_encoder(BP.PORT_A):6d}  B: {BP.get_motor_encoder(BP.PORT_B):6d}  C: {BP.get_motor_encoder(BP.PORT_C):6d}  D: {BP.get_motor_encoder(BP.PORT_D):6d}")
        except IOError as error:
            print(error)

        time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
