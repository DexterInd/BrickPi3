#!/usr/bin/env python
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for reading a Dexter Industries temperature sensor connected to PORT_1 of the BrickPi3
# 
# Hardware: Connect .
# 
# Results:  When you run this program, .

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

import math

# temperature conversion lists
_a = [0.003357042,         0.003354017,        0.0033530481,       0.0033536166]
_b = [0.00025214848,       0.00025617244,      0.00025420230,      0.000253772]
_c = [0.0000033743283,     0.0000021400943,    0.0000011431163,    0.00000085433271]
_d = [-0.000000064957311, -0.000000072405219, -0.000000069383563, -0.000000087912262]

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.CUSTOM, [(BP.SENSOR_CUSTOM.PIN1_ADC)]) # Configure for a Dexter Industries temperature sensor (analog on sensor port pin 1).

try:
    while True:
        # read the sensor value
        # BP.get_sensor retrieves a sensor value.
        # BP.get_sensor returns a list of 4 values.
        #     The first is the pin 1 analog line value (what we want to display).
        #     The second is the pin 6 analog line value.
        #     The third is the pin 5 digital value.
        #     The third is the pin 6 digital value.
        try:
            value = BP.get_sensor(BP.PORT_1)[0] # read the sensor port values
            if(value < 4095): # if the value is < 4095, the sensor is connected
                # do the conversion from the raw value to degrees C
                RtRt25 = (float)(value) / (4095 - value)
                lnRtRt25 = math.log(RtRt25)
                
                if (RtRt25 > 3.277) :
                    i = 0
                elif (RtRt25 > 0.3599) :
                    i = 1
                elif (RtRt25 > 0.06816) :
                    i = 2
                else :
                    i = 3
                
                temp =  1.0 / (_a[i] + (_b[i] * lnRtRt25) + (_c[i] * lnRtRt25 * lnRtRt25) + (_d[i] * lnRtRt25 * lnRtRt25 * lnRtRt25))
                temp = temp - 273.15
                print("Temperature: %.1fC" % temp) # print the temperature in degrees C
            else:             # else the value is 4095, so the sensor is disconnected
                print("Temperature: (disconnected)")
        except brickpi3.SensorError as error:
            print(error)
        
        time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
