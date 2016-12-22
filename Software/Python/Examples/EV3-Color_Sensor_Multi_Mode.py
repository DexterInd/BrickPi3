#!/usr/bin/env python
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for reading an EV3 color sensor connected to PORT_1 of the BrickPi3
# 
# Hardware: Connect an EV3 color sensor to BrickPi3 sensor port 1.
# 
# Results:  When you run this program, after the sensor is configured (can take up to about 5 seconds), it will rapidly switch between modes, taking readings, and then it will print the values.

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

# Configure for an EV3 color sensor.
# BP.set_sensor_type configures the BrickPi3 for a specific sensor.
# BP.PORT_1 specifies that the sensor will be on sensor port 1.
# BP.Sensor_TYPE.EV3_COLOR_REFLECTED specifies that the sensor will be an ev3 color sensor.
BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_COLOR_REFLECTED) # Configure for an EV3 color sensor.

try:
    # BP.get_sensor retrieves a sensor value.
    # BP.PORT_1 specifies that we are looking for the value of sensor port 1.
    # BP.get_sensor returns a list of two values.
    #     The first item in the list is the sensor value (what we want to display).
    #     The second item in the list is the error value (should be equal to BP.SUCCESS if the sensor is configured and the value was read successfully)
    print("Configuring...")
    error = -1
    while error != BP.SUCCESS:
        error = BP.get_sensor(BP.PORT_1)[1] # while the sensor is being configured
        print(error)
        time.sleep(0.1)                     # wait
    print("Configured.")
    
    while True:
        BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_COLOR_REFLECTED)        # Configure for an EV3 color sensor in reflected mode.
        time.sleep(0.02)
        value1 = BP.get_sensor(BP.PORT_1)[0]                                     # get the sensor value
        BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_COLOR_AMBIENT)          # Configure for an EV3 color sensor in ambient mode.
        time.sleep(0.02)
        value2 = BP.get_sensor(BP.PORT_1)[0]                                     # get the sensor value
        BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_COLOR_COLOR)            # Configure for an EV3 color sensor in color mode.
        time.sleep(0.02)
        value3 = BP.get_sensor(BP.PORT_1)[0]                                     # get the sensor value
        BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_COLOR_COLOR_COMPONENTS) # Configure for an EV3 color sensor in color components mode.
        time.sleep(0.02)
        value4 = BP.get_sensor(BP.PORT_1)[0]                                     # get the sensor value
        print(value1, "   ", value2, "   ", value3, "   ", value4)               # print the color sensor values

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
