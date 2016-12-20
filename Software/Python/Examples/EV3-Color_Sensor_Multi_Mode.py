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

BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_COLOR_REFLECTED) # Configure for an EV3 color sensor.

try:
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
        value1 = BP.get_sensor(BP.PORT_1)[0]
        BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_COLOR_AMBIENT)          # Configure for an EV3 color sensor in ambient mode.
        time.sleep(0.02)
        value2 = BP.get_sensor(BP.PORT_1)[0]
        BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_COLOR_COLOR)            # Configure for an EV3 color sensor in color mode.
        time.sleep(0.02)
        value3 = BP.get_sensor(BP.PORT_1)[0]
        BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_COLOR_COLOR_COMPONENTS) # Configure for an EV3 color sensor in color components mode.
        time.sleep(0.02)
        value4 = BP.get_sensor(BP.PORT_1)[0]
        print(value1, "   ", value2, "   ", value3, "   ", value4)               # print the color sensor values
except KeyboardInterrupt:
    BP.reset_all()