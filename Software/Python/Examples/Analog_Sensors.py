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
BP.set_sensor_type(BP.PORT_2, BP.SENSOR_TYPE.CUSTOM, [(BP.SENSOR_CUSTOM.PIN1_ADC)]) # Configure for an analog on sensor port pin 1.
BP.set_sensor_type(BP.PORT_3, BP.SENSOR_TYPE.CUSTOM, [(BP.SENSOR_CUSTOM.PIN1_ADC)]) # Configure for an analog on sensor port pin 1.
BP.set_sensor_type(BP.PORT_4, BP.SENSOR_TYPE.CUSTOM, [(BP.SENSOR_CUSTOM.PIN1_ADC)]) # Configure for an analog on sensor port pin 1.

try:
    while True:
        value1 = BP.get_sensor(BP.PORT_1)[0][0] # read the sensor port value
        value2 = BP.get_sensor(BP.PORT_2)[0][0] # read the sensor port value
        value3 = BP.get_sensor(BP.PORT_3)[0][0] # read the sensor port value
        value4 = BP.get_sensor(BP.PORT_4)[0][0] # read the sensor port value
        ref5v = (4095.0 / BP.get_voltage_5v()[0])
        print("1R: %4d  1V: %5.3fV  2R: %4d  2V: %5.3fV  3R: %4d  3V: %5.3fV  4R: %4d  4V: %5.3fV" % (value1, (value1 / ref5v), value2, (value2 / ref5v), value3, (value3 / ref5v), value4, (value4 / ref5v))) # print the value
        time.sleep(0.02)                       # delay 20ms
except KeyboardInterrupt:
    BP.reset_all()