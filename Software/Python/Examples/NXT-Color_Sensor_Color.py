#!/usr/bin/env python
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for reading an NXT color sensor connected to PORT_1 of the BrickPi3
# 
# Hardware: Connect an NXT color sensor to BrickPi3 Port 1.
# 
# Results:  When you run this program, you should see the detected color and the raw values for red, green, blue, and ambient.

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

# Configure for an NXT color sensor.
# BP.set_sensor_type configures the BrickPi3 for a specific sensor.
# BP.PORT_1 specifies that the sensor will be on sensor port 1.
# BP.SENSOR_TYPE.NXT_COLOR_FULL specifies that the sensor will be an NXT color sensor.
BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.NXT_COLOR_FULL)

color = ["Black", "Blue", "Green", "Yellow", "Red", "White"]

try:
    while True:
        # read and display the sensor value
        # BP.get_sensor retrieves a sensor value.
        # BP.PORT_1 specifies that we are looking for the value of sensor port 1.
        # BP.get_sensor returns the sensor value (what we want to display).
        try:
            value = BP.get_sensor(BP.PORT_1)
            if(value[0] >= 1 and value[0] <= 6 and len(value) == 5): # successfully read the values
                print(color[value[0] - 1], value)                    # print the values
            else:
                print("error reading color sensor values from BrickPi3")
        except brickpi3.SensorError as error:
            print(error)
        
        time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
