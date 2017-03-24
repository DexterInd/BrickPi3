#!/usr/bin/env python
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for reading an analog sensor connected to PORT_1 of the BrickPi3
# 
# Hardware: Connect an analog sensor (or more than one) (such as an NXT touch, light, or sound sensor) to one or more sensor ports of the BrickPi3.
# 
# Results:  When you run this program, you will see the raw sensor value as well as the sensor voltage for all four sensor ports.

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

# configure all four sensor ports as an analog sensor, polling the pin 1 analog line
BP.set_sensor_type(BP.PORT_1 + BP.PORT_2 + BP.PORT_3 + BP.PORT_4, BP.SENSOR_TYPE.CUSTOM, [(BP.SENSOR_CUSTOM.PIN1_ADC)])

try:
    while True:
        # read the sensor value for each port
        # BP.get_sensor retrieves a sensor value.
        # BP.get_sensor returns a list of 4 values.
        #     The first is the pin 1 analog line value (what we want to display).
        #     The second is the pin 6 analog line value.
        #     The third is the pin 5 digital value.
        #     The third is the pin 6 digital value.
        try:
            value1 = BP.get_sensor(BP.PORT_1)[0]
            value2 = BP.get_sensor(BP.PORT_2)[0]
            value3 = BP.get_sensor(BP.PORT_3)[0]
            value4 = BP.get_sensor(BP.PORT_4)[0]
            
            ref5v = (4095.0 / BP.get_voltage_5v()) # read the reference to determine the analog sensor voltage
            print("1R: %4d  1V: %5.3fV  2R: %4d  2V: %5.3fV  3R: %4d  3V: %5.3fV  4R: %4d  4V: %5.3fV" % (value1, (value1 / ref5v), value2, (value2 / ref5v), value3, (value3 / ref5v), value4, (value4 / ref5v))) # print the values
        
        except brickpi3.SensorError as error:
            print(error)
        
        time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
