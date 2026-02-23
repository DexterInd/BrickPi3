#!/usr/bin/env python3
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2026 Modular Robotics Inc
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for reading a touch sensor connected to PORT_1 of the BrickPi3
#
# Hardware: Connect an EV3 or NXT touch sensor to BrickPi3 Port 1.
#
# Results:  When you run this program, you should see a 0 when the touch sensor is not pressed, and a 1 when the touch sensor is pressed.

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.


# Configure all 4 ports for touch sensors
PORTS = [BP.PORT_1, BP.PORT_2, BP.PORT_3, BP.PORT_4]
for port in PORTS:
    BP.set_sensor_type(port, BP.SENSOR_TYPE.TOUCH)

print("Connect a touch sensor to any sensor port (S1-S4), press and release the touch sensor.")
print("Press Ctrl+C to exit once done.")

try:
    while True:
        # Display all port values in one line
        port_status = []
        for idx, port in enumerate(PORTS, start=1):
            try:
                value = BP.get_sensor(port)
            except brickpi3.SensorError:
                value = 'Err'
            port_status.append(f"PORT_{idx}: {value}")
        print(", ".join(port_status))
        time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
