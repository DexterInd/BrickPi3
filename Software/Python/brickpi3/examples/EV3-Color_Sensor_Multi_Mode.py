#!/usr/bin/env python3
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2026 Modular Robotics Inc
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for reading an EV3 color sensor connected to PORT_1 of the BrickPi3
#
# Hardware: Connect an EV3 color sensor to BrickPi3 sensor port 1.
#
# Results:  When you run this program, after the sensor is configured (can take up to about 5 seconds), it will rapidly switch between modes, taking readings, and then it will print the values.


print("\nUSER INSTRUCTIONS:")
print("Connect the EV3 color sensor to BrickPi3 sensor port 1.")
print("This program will rapidly switch between sensor modes and print the values.")
input("Press Enter to continue...")

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

try:
    BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.
except Exception as error:
    print(f"Failed to initialize BrickPi3: {error}")
    print("Please check that the BrickPi3 is properly connected and powered.")
    exit(1)



# Configure for an EV3 color sensor.
# BP.set_sensor_type configures the BrickPi3 for a specific sensor.
# BP.PORT_1 specifies that the sensor will be on sensor port 1.
# BP.Sensor_TYPE.EV3_COLOR_REFLECTED specifies that the sensor will be an ev3 color sensor.
BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_COLOR_REFLECTED)

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

    # First loop: allow sensor time to connect and stabilize (up to 1 minute)
    print("Waiting for sensor to stabilize (up to 1 minute)...")
    start_time = time.time()
    while time.time() - start_time < 60:
        try:
            value = BP.get_sensor(BP.PORT_1)
            print(".", end="", flush=True)
            if value is not None:
                break
        except brickpi3.SensorError:
            print(".", end="", flush=True)
        time.sleep(0.2)
    print("\nSensor ready. Starting mode switching.")

    while True:
        BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_COLOR_REFLECTED)
        time.sleep(0.02)
        try:
            value1 = BP.get_sensor(BP.PORT_1)
        except (brickpi3.SensorError, OSError) as error:
            value1 = f"Error: {error}"

        BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_COLOR_AMBIENT)
        time.sleep(0.02)
        try:
            value2 = BP.get_sensor(BP.PORT_1)
        except (brickpi3.SensorError, OSError) as error:
            value2 = f"Error: {error}"

        BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_COLOR_COLOR)
        time.sleep(0.02)
        try:
            value3 = BP.get_sensor(BP.PORT_1)
        except (brickpi3.SensorError, OSError) as error:
            value3 = f"Error: {error}"

        BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_COLOR_COLOR_COMPONENTS)
        time.sleep(0.02)
        try:
            value4 = BP.get_sensor(BP.PORT_1)
        except (brickpi3.SensorError, OSError) as error:
            value4 = f"Error: {error}"

        print(value1, "   ", value2, "   ", value3, "   ", value4)

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
