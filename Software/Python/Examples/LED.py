# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for controlling the BrickPi3 LED

from __future__ import print_function
from __future__ import division

import time
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3()

try:
    while True:
        for i in range(101):
            BP.set_led(i)
            time.sleep(0.01) # delay 100ms
        for i in range(101):
            BP.set_led(100 - i)
            time.sleep(0.01) # delay 100ms
except KeyboardInterrupt:
    BP.reset_all()       # give control of the LED back to the Firmware