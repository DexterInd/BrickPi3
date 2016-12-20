#!/bin/bash
echo "Updating the BrickPi3 SAMD Firmware with '/home/pi/Dexter/BrickPi3/Firmware/brickpi3_firmware.bin'."
sudo openocd -f interface/raspberrypi2-native.cfg -c "transport select swd; set CHIPNAME at91samd21j18; source [find target/at91samdXX.cfg]; adapter_khz 250; adapter_nsrst_delay 100; adapter_nsrst_assert_width 100" -c "init; targets; reset halt; program /home/pi/Dexter/BrickPi3/Firmware/brickpi3_firmware.bin verify; reset" -c "shutdown"
