#!/usr/bin/env python3
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2026 Modular Robotics Inc
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for reading an analog sensor connected to PORT_1 of the BrickPi3
#
# Hardware: Connect an analog sensor (such as an NXT touch, light, or sound sensor) to sensor port 1 of the BrickPi3.
#
# Results:  When you run this program, you will see the raw sensor value as well as the sensor voltage.

print("""
INSTRUCTIONS:
Connect an analog sensor (such as an NXT touch, light, or sound sensor) to sensor port 1 of the BrickPi3.
This program will display the raw sensor value and the sensor voltage in real time.

Press the ENTER key to start testing.
Press Ctrl+C to stop.
""")

input("Press ENTER when you're ready...")

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.CUSTOM, [(BP.SENSOR_CUSTOM.PIN1_ADC)]) # Configure for an analog on sensor port pin 1, and poll the analog line on pin 1.
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
        # read the sensor value
        # BP.get_sensor retrieves a sensor value.
        # BP.PORT_1 specifies that we are looking for the value of sensor port 1.
        # BP.get_sensor returns a list of 4 values.
        #     The first is the pin 1 analog line value (what we want to display).
        #     The second is the pin 6 analog line value.
        #     The third is the pin 5 digital value.
        #     The fourth is the pin 6 digital value.
        try:
            value = BP.get_sensor(BP.PORT_1)[0] # read the sensor port value
            voltage = value / (4095.0 / BP.get_voltage_5v())
            print(f"Raw value: {value:4d}   Voltage: {voltage:5.3f}v")
        except brickpi3.SensorError as error:
            print(f"Sensor error: {error}")
        time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.
except KeyboardInterrupt:
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
except Exception as e:
    print(f"Unexpected error: {e}")
    BP.reset_all()
