# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for reading an EV3 color sensor connected to PORT_1 of the BrickPi3

from __future__ import print_function
from __future__ import division

import time
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3()

BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_COLOR_COLOR_COMPONENTS) # Configure for an EV3 color sensor.
#BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_COLOR_RAW_REFLECTED) # Configure for an EV3 color sensor.

try:
    while True:
        print(BP.get_sensor(BP.PORT_1)[0]) # print the color
        time.sleep(0.02)         # delay 20ms
except KeyboardInterrupt:
    BP.reset_all()