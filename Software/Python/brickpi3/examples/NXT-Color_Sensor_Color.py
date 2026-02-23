#!/usr/bin/env python3
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2026 Modular Robotics Inc
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for reading an NXT color sensor connected to PORT_1 of the BrickPi3
#
# Hardware: Connect an NXT color sensor to BrickPi3 Port 1.
#
# Results:  When you run this program, you should see the detected color and the raw values for red, green, blue, and ambient.

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

# Configure for an NXT color sensor.
# BP.set_sensor_type configures the BrickPi3 for a specific sensor.
# BP.PORT_1 specifies that the sensor will be on sensor port 1.
# BP.SENSOR_TYPE.NXT_COLOR_FULL specifies that the sensor will be an NXT color sensor.
BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.NXT_COLOR_FULL)

color = ["Black", "Blue", "Green", "Yellow", "Red", "White"]

print("NXT Color Sensor Example")
print("========================")
print("This program reads color values from an NXT color sensor.")
print("Make sure an NXT color sensor is connected to BrickPi3 Port 1.")
print()
print("Instructions:")
print("- Press ENTER to take a color reading")
print("- Press Ctrl+C to exit the program")
print()
input("Press ENTER to start taking readings...")

try:
    while True:
        # read and display the sensor value
        # BP.get_sensor retrieves a sensor value.
        # BP.PORT_1 specifies that we are looking for the value of sensor port 1.
        # BP.get_sensor returns the sensor value (what we want to display).
        try:
            value = BP.get_sensor(BP.PORT_1)
            if(value[0] >= 1 and value[0] <= 6 and len(value) == 5): # successfully read the values
                detected_color = color[value[0] - 1]
                print(f"Detected Color: {detected_color:8} | Raw Values - Red: {value[1]:04.0f}, Green: {value[2]:04.0f}, Blue: {value[3]:04.0f}, Ambient: {value[4]:04.0f}")
            else:
                print("Error: Unable to read color sensor values from BrickPi3")
        except brickpi3.SensorError as error:
            print(f"Sensor Error: {error}")

        time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    print("\nProgram stopped by user.")
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
    print("BrickPi3 reset successfully.")
