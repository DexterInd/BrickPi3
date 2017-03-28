#!/usr/bin/env python
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for controlling the BrickPi3 LED
#
# Results:  When you run this program, the BrickPi3 LED will fade up and down.

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

try:
    while True:
        for i in range(101):    # count from 0-100
            BP.set_led(i)       # set the LED brightness (0 to 100)
            time.sleep(0.01)    # delay for 0.1 seconds (100ms) to reduce the Raspberry Pi CPU load and give time to see the LED pulsing.
        
        for i in range(101):    # count from 0-100
            BP.set_led(100 - i) # set the LED brightness (100 to 0)
            time.sleep(0.01)     # delay for 0.1 seconds (100ms) to reduce the Raspberry Pi CPU load and give time to see the LED pulsing.

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
