#!/usr/bin/env python3
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2026 Modular Robotics Inc
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for changing the address of a BrickPi3

print("\nUSER INSTRUCTIONS:")
print("This script sets addresses for BrickPi3 devices in a stack configuration.")
print("Multiple BrickPi3 units can be connected together and assigned unique addresses.")
print("You will need to modify the serial number IDs in the code to match your devices.")
print("Use the Read_Info.py example to find the serial number of each BrickPi3 unit.")
input("Press Enter to continue...")

import brickpi3 # import the BrickPi3 drivers

# Map of address -> serial number for the BrickPi3 units to configure.
# Valid addresses are 1, 2, 3, and 4. Address 1 is the default address.
# Include only the units you want to set; comment out the others.
# Use Read_Info.py to find the serial number of each BrickPi3 unit.
SERIAL_NUMBERS = {
    1: "3B21D237504D5741372E3120FF0E2910",  # default address (use to reset a unit back to address 1)
    # 2: "3B21D237504D5741372E3120FF0E2910",
    # 3: "192A0F96514D4D5438202020FF080C23",
    # 4: "84FBCC9D514D4D5439202020FF0E070F",
}

if not SERIAL_NUMBERS:
    raise ValueError("SERIAL_NUMBERS must contain at least one entry.")
if not all(addr in (1, 2, 3, 4) for addr in SERIAL_NUMBERS):
    raise ValueError("Addresses must be 1, 2, 3, or 4.")

# Assign addresses for only the specified units
for address, serial in SERIAL_NUMBERS.items():
    brickpi3.set_address(address, serial)

try:
    bp3_instances = {address: brickpi3.BrickPi3(address) for address in SERIAL_NUMBERS}

    for address, bp in bp3_instances.items():
        print(f"\nBrickPi3 Address: {address}")
        print(f"Manufacturer    : {bp.get_manufacturer()}")
        print(f"Board           : {bp.get_board()}")
        print(f"Serial Number   : {bp.get_id()}")
        print(f"Hardware version: {bp.get_version_hardware()}")
        print(f"Firmware version: {bp.get_version_firmware()}")
        print(f"Battery voltage : {bp.get_voltage_battery()}")
        print(f"9v voltage      : {bp.get_voltage_9v()}")
        print(f"5v voltage      : {bp.get_voltage_5v()}")
        print(f"3.3v voltage    : {bp.get_voltage_3v3()}")

except IOError as error:
    print(error)

except brickpi3.FirmwareVersionError as error:
    print(error)
