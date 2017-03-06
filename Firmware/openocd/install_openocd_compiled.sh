#!/bin/bash

REPO_PATH=$(sudo find / -name "BrickPi3" | head -1)
# unzip the compiled OpenOCD
unzip $REPO_PATH/Firmware/openocd/openocd_compiled.zip -d $REPO_PATH/Firmware/openocd

# Put the configuration files into /usr/local/share
sudo cp -rn $REPO_PATH/Firmware/openocd/openocd_compiled/files/openocd /usr/local/share

# Put the openocd binary into /usr/bin
sudo cp -rn $REPO_PATH/Firmware/openocd/openocd_compiled/openocd /usr/bin

# Make the openocd binary executable
sudo chmod +x /usr/bin/openocd

# Remove the unzipped files
rm -rf $REPO_PATH/Firmware/openocd/openocd_compiled
