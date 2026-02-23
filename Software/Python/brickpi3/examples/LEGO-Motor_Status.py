#!/usr/bin/env python3
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2026 Modular Robotics Inc
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for reading the status of a motor.
#
# Hardware: Connect an EV3 or NXT motor to the BrickPi3 motor port A.
#
# Results:  When you run this program, the status of motor A will be printed.

print("USER INSTRUCTIONS:")
print("This program reads and displays the status of a motor connected to port A.")
print("")
print("HARDWARE SETUP:")
print("1. Connect your BrickPi3 to a Raspberry Pi")
print("2. Connect a 9V or 12V power supply to the BrickPi3")
print("3. Connect an EV3 or NXT motor to BrickPi3 motor port A")
print("")
print("PROGRAM BEHAVIOR:")
print("- The program will continuously read and display the motor status")
print("- Status information includes:")
print("  * Motor flags (low voltage, overloaded, etc.)")
print("  * Motor power level (-128 = MOTOR_FLOAT, meaning unpowered)")
print("  * Motor position (encoder value)")
print("  * Motor speed (degrees per second)")
print("- The display updates every 20ms")
print("- Press Ctrl+C to stop the program")
print("")
print("NOTE: Power will show -128 (MOTOR_FLOAT) since no power commands are sent.")
print("You can manually turn the motor to see position and speed values change.")
print("")
input("Press Enter to continue...")

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

try:
    while True:
        try:
            status = BP.get_motor_status(BP.PORT_A)
            print(f"Flags: 0x{status[0]:02X}, Power: {status[1]:4d}, Position: {status[2]:6d}, DPS: {status[3]:4d}")
        except IOError as error:
            print(error)

        time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
