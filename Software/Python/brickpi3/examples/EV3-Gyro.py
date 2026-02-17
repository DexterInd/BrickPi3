#!/usr/bin/env python3
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2026 Modular Robotics Inc
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for reading an EV3 gyro sensor connected to PORT_1 of the BrickPi3
#
# Hardware: Connect an EV3 gyro sensor to BrickPi3 sensor port 1.
#
# Results:  When you run this program, the gyro's absolute rotation and rate of rotation will be printed.

print("\nUSER INSTRUCTIONS:")
print("Connect the EV3 gyro sensor to BrickPi3 sensor port 1.")
print("This program will continuously print the gyro's absolute rotation and rate of rotation.")
input("Press Enter to continue...")

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.



# Configure for an EV3 color sensor.
# BP.set_sensor_type configures the BrickPi3 for a specific sensor.
# BP.PORT_1 specifies that the sensor will be on sensor port 1.
# BP.Sensor_TYPE.EV3_GYRO_ABS_DPS specifies that the sensor will be an EV3 gyro sensor.
BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_GYRO_ABS_DPS)

# Pre-loop: Poll sensor until valid reading or 1 min elapsed
print("Waiting for valid sensor reading (up to 1 minute)...")
start_time = time.time()
valid_reading = False
while time.time() - start_time < 60:
    try:
        value = BP.get_sensor(BP.PORT_1)
        print(".", end="", flush=True)
        if value is not None:
            print(".", end="", flush=True)
            valid_reading = True
            break
    except (brickpi3.SensorError, OSError):
        print(".", end="", flush=True)
    time.sleep(0.2)
if not valid_reading:
    print("\nNo valid sensor reading received after 1 minute. Exiting.")
    exit(1)

try:


    while True:
        # BP.get_sensor retrieves a sensor value.
        # BP.PORT_1 specifies that we are looking for the value of sensor port 1.
        # BP.get_sensor returns the sensor value (what we want to display).
        try:
            print(BP.get_sensor(BP.PORT_1))   # print the gyro sensor values
        except brickpi3.SensorError as error:
            print(error)

        time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
