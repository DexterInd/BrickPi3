# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for reading an analog sensor connected to PORT_1 of the BrickPi3

from __future__ import print_function
from __future__ import division

import time
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3()

BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.CUSTOM, [(BP.SENSOR_CUSTOM.PIN1_ADC)]) # Configure for an analog on sensor port pin 1.

try:
    while True:
        value = BP.get_sensor(BP.PORT_1)[0][0] # read the sensor port value
        print("Raw value: %4d   Voltage: %5.3fv" % (value, (value / (4095.0 / BP.get_voltage_5v()[0])))) # print the value
        time.sleep(0.02)                       # delay 20ms
except KeyboardInterrupt:
    BP.reset_all()