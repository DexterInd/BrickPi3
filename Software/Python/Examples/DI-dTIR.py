# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for reading a Dexter Industries Thermal Infrared sensor connected to PORT_1 of the BrickPi3

from __future__ import print_function
from __future__ import division

import time
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3()

BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.I2C, [0, 20]) # Configure for a Dexter Industries Thermal Infrared sensor (I2C device).

TIR_I2C_ADDR        = 0x0E      # TIR I2C device address 
TIR_AMBIENT         = 0x00      # Ambient Temp
TIR_OBJECT          = 0x01      # Object Temp
TIR_SET_EMISSIVITY  = 0x02      
TIR_GET_EMISSIVITY  = 0x03
TIR_CHK_EMISSIVITY  = 0x04
TIR_RESET           = 0x05

try:
    while True:
        BP.transact_i2c(BP.PORT_1, TIR_I2C_ADDR, [TIR_OBJECT], 2)
        time.sleep(0.01)          # delay 10ms
        value, error = BP.get_sensor(BP.PORT_1) # read the sensor port values
        if not error:
            temp = (float)((value[1] << 8) + value[0])  #join the MSB and LSB part
            temp = temp * 0.02 - 0.01        #Converting to Celcius
            temp = temp - 273.15
            print("Object Temp: %.1fC" % temp) # print the value
        
        BP.transact_i2c(BP.PORT_1, TIR_I2C_ADDR, [TIR_AMBIENT], 2)
        time.sleep(0.01)          # delay 10ms
        value, error = BP.get_sensor(BP.PORT_1) # read the sensor port values
        if not error:
            temp = (float)((value[1] << 8) + value[0])  #join the MSB and LSB part
            temp = temp * 0.02 - 0.01        #Converting to Celcius
            temp = temp - 273.15
            print("Ambient Temp: %.1fC" % temp) # print the value
        
        time.sleep(0.02)          # delay 20ms
except KeyboardInterrupt:
    BP.reset_all()