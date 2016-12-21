# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for running all motors while a touch sensor connected to PORT_1 of the BrickPi3 is being pressed.

from __future__ import print_function
from __future__ import division

import time
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3()

BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.TOUCH) # Configure for a touch sensor. If an EV3 touch sensor is connected, it will be configured for EV3 touch, otherwise it's configured for NXT touch.

try:
    print("Press touch sensor on port 1 to run motors")
    while not BP.get_sensor(BP.PORT_1)[0]:
        time.sleep(0.02)
    
    speed = 0
    adder = 1
    while True:
        if BP.get_sensor(BP.PORT_1)[0]:
            if speed <= -100 or speed >= 100:
                adder = -adder
            speed += adder
        else:
            speed = 0
            adder = 1
        BP.set_motor_speed(BP.PORT_A, speed)
        BP.set_motor_speed(BP.PORT_B, speed)
        BP.set_motor_speed(BP.PORT_C, speed)
        BP.set_motor_speed(BP.PORT_D, speed)
        print("Encoder A: %6d  B: %6d  C: %6d  D: %6d" % (BP.get_motor_encoder(BP.PORT_A)[0], BP.get_motor_encoder(BP.PORT_B)[0], BP.get_motor_encoder(BP.PORT_C)[0], BP.get_motor_encoder(BP.PORT_D)[0]))
        time.sleep(0.02)                   # delay 20ms
except KeyboardInterrupt:
    BP.reset_all()