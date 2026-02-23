#!/usr/bin/env python3
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2026 Modular Robotics Inc
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for running a motor to a target position set by the encoder of another motor.
#
# Hardware: Connect EV3 or NXT motors to the BrickPi3 motor ports A and D. Make sure that the BrickPi3 is running on a 9v power supply.
#
# Results:  When you run this program, motor A will run to match the position of motor D. Manually rotate motor D, and motor A will follow.

print("USER INSTRUCTIONS:")
print("Connect EV3 or NXT motors to BrickPi3 motor ports A and D.")
print("Make sure the BrickPi3 is running on a 9V power supply.")
print("This program will make motor A follow the position of motor D.")
print("Motor D will be set to float mode for manual rotation.")
print("Manually rotate motor D to see motor A follow its position.")
print("The program will display motor A target and position continuously.")
print("Press Ctrl+C to stop the program.")
print("Press Enter to continue...")
input()

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

try:
    try:
        BP.offset_motor_encoder(BP.PORT_A, BP.get_motor_encoder(BP.PORT_A)) # reset encoder A
        BP.offset_motor_encoder(BP.PORT_D, BP.get_motor_encoder(BP.PORT_D)) # reset encoder D
    except IOError as error:
        print(error)

    BP.set_motor_power(BP.PORT_D, BP.MOTOR_FLOAT)    # float motor D
    BP.set_motor_limits(BP.PORT_A, 50, 200)          # optionally set a power limit (in percent) and a speed limit (in Degrees Per Second)
    while True:
        # Each of the following BP.get_motor_encoder functions returns the encoder value.
        try:
            target = BP.get_motor_encoder(BP.PORT_D) # read motor D's position
        except IOError as error:
            print(error)

        BP.set_motor_position(BP.PORT_A, target)    # set motor A's target position to the current position of motor D

        try:
            print(f"Motor A target: {target:6d}  Motor A position: {BP.get_motor_encoder(BP.PORT_A):6d}")
        except IOError as error:
            print(error)

        time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
