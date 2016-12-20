# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for running a motor to a target position set by the encoder of another motor.

from __future__ import print_function
from __future__ import division

import time
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3()

try:
    while True:
        target = BP.get_motor_encoder(BP.PORT_B)[0]
        BP.set_motor_position(BP.PORT_C, target)
        print("Motor C target: %6d  Motor C position: %6d" % (target, BP.get_motor_encoder(BP.PORT_C)[0]))
        time.sleep(0.02)                   # delay 20ms
except KeyboardInterrupt:
    BP.reset_all()