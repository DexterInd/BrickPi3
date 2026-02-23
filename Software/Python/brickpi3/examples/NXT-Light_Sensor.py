#!/usr/bin/env python3
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2026 Modular Robotics Inc
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for reading an NXT light sensor connected to PORT_1 of the BrickPi3
#
# Hardware: Connect an NXT light sensor to BrickPi3 Port 1.
#
# Results:  When you run this program, you should see the value from the light sensor.

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

# Configure for an NXT light sensor.
# BP.set_sensor_type configures the BrickPi3 for a specific sensor.
# BP.PORT_1 specifies that the sensor will be on sensor port 1.
# BP.SENSOR_TYPE.NXT_LIGHT_ON specifies that the sensor will be an NXT light sensor.
BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.NXT_LIGHT_OFF)

print("NXT Light Sensor Example")
print("========================")
print("This program reads light values from an NXT light sensor.")
print("Make sure an NXT light sensor is connected to BrickPi3 Port 1.")
print()
print("Instructions:")
print("- Press Ctrl+C to exit the program")
input("Press ENTER to start taking readings...")

try:
    while True:
        # read and display the sensor value
        # BP.get_sensor retrieves a sensor value.
        # BP.PORT_1 specifies that we are looking for the value of sensor port 1.
        # BP.get_sensor returns the sensor value (what we want to display).
        try:
            value = BP.get_sensor(BP.PORT_1)
            print(f"Light Value: {value:03.0f}")
        except brickpi3.SensorError as error:
            print(f"Sensor Error: {error}")

        time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    print("\nProgram stopped by user.")
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
    print("BrickPi3 reset successfully.")
