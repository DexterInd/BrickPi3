To update the BrickPi3 Firmware
-------------------------------
Connect the BrickPi3 to a Raspberry Pi. Assuming you've set up the BrickPi3 software by running the install.sh script, everything should be ready for you to update the firmware by running the script "/home/pi/Dexter/BrickPi3/Firmware/brickpi3samd_flash_firmware.sh".

Towards the bottom of the output (third line from the end), you should see something like ** Verified OK ** which means the firmware was flashed and verified successfully.

You can run the example program "Read_Voltage_And_Info.py" in "BrickPi3/Software/Python/Examples" to make sure that the FW version is correct (version "0.0.3" as of writing this).
