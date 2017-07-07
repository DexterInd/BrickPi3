#!/usr/bin/env python
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for reading a Dexter Industries Thermal Infrared sensor connected to PORT_1 of the BrickPi3
# 
# Hardware: Connect a Dexter Industries Thermal Infared sensor to sensor port 1 of the BrickPi3.
# 
# Results:  When you run this program, the TIR temperature and ambient temperature will be read and displayed.

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.I2C, [0, 20]) # Configure for a Dexter Industries Thermal Infrared sensor (I2C device). No special settings, 20 microseconds minimum between I2C transitions.

TIR_I2C_ADDR        = 0x0E      # TIR I2C device address 
TIR_AMBIENT         = 0x00      # Ambient Temp
TIR_OBJECT          = 0x01      # Object Temp
TIR_SET_EMISSIVITY  = 0x02      
TIR_GET_EMISSIVITY  = 0x03
TIR_CHK_EMISSIVITY  = 0x04
TIR_RESET           = 0x05

try:
    while True:
        # Perform an I2C transaction on sensor port 1, using the TIR's I2C address, writing TIR_OBJECT (to set the register to read from), and reading 2 bytes.
        BP.transact_i2c(BP.PORT_1, TIR_I2C_ADDR, [TIR_OBJECT], 2)
        time.sleep(0.01)                               # delay 10ms so that the BrickPi3 has time to make the I2C transaction.
        
        # read the sensor value
        # BP.get_sensor retrieves a sensor value.
        # BP.PORT_1 specifies that we are looking for the value of sensor port 1.
        # BP.get_sensor returns a list of the I2C bytes read from the sensor.
        try:
            value = BP.get_sensor(BP.PORT_1)           # read the sensor values
            temp = (float)((value[1] << 8) + value[0]) # join the MSB and LSB part
            temp = temp * 0.02 - 0.01                  # Converting to Celcius
            temp = temp - 273.15                       #          ''
            print("Object Temp: %.1fC" % temp)         # print the temperature
        except brickpi3.SensorError as error:
            print(error)
        
        BP.transact_i2c(BP.PORT_1, TIR_I2C_ADDR, [TIR_AMBIENT], 2)
        time.sleep(0.01)                               # delay 10ms so that the BrickPi3 has time to make the I2C transaction.
        try:
            value = BP.get_sensor(BP.PORT_1)           # read the sensor values
            temp = (float)((value[1] << 8) + value[0]) # join the MSB and LSB part
            temp = temp * 0.02 - 0.01                  # Converting to Celcius
            temp = temp - 273.15                       #          ''
            print("Ambient Temp: %.1fC" % temp)        # print the temperature
        except brickpi3.SensorError as error:
            print(error)
        
        time.sleep(0.2)

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
