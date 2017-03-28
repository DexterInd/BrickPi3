#!/usr/bin/env python
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for changing the address of a BrickPi3

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

brickpi3.set_address(2, "") # set all attached BrickPi3s to address 2
#brickpi3.set_address(3, "192A0F96514D4D5438202020FF080C23") # set BrickPi3 with serial number ID "192A0F96514D4D5438202020FF080C23" to address 3

try:
    BP = brickpi3.BrickPi3(2) # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.
    
    # Each of the following BP.get functions return a value that we want to display.
    print("Manufacturer    : ", BP.get_manufacturer()    ) # read and display the serial number
    print("Board           : ", BP.get_board()           ) # read and display the serial number
    print("Serial Number   : ", BP.get_id()              ) # read and display the serial number
    print("Hardware version: ", BP.get_version_hardware()) # read and display the hardware version
    print("Firmware version: ", BP.get_version_firmware()) # read and display the firmware version
    print("Battery voltage : ", BP.get_voltage_battery() ) # read and display the current battery voltage
    print("9v voltage      : ", BP.get_voltage_9v()      ) # read and display the current 9v regulator voltage
    print("5v voltage      : ", BP.get_voltage_5v()      ) # read and display the current 5v regulator voltage
    print("3.3v voltage    : ", BP.get_voltage_3v3()     ) # read and display the current 3.3v regulator voltage
    
except IOError as error:
    print(error)

except brickpi3.FirmwareVersionError as error:
    print(error)
