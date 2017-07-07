#! /bin/bash
# determine repo path (install directory)
REPO_PATH=$(readlink -f $(dirname $0) | grep -E -o "^(.*?\\BrickPi3)")

# specify full file name, including repo path
FILE="$REPO_PATH/Firmware/brickpi3_firmware.bin"

# make sure the firmware file exists
if [ -f "$FILE" ]; then
    echo "Updating the BrickPi3 SAMD Firmware with '$FILE'"
    
    # check the RPi version
    RPI_VERSION=$(python -c "import auto_detect_rpi; print auto_detect_rpi.getRPIGenerationCode()")
    # set default to RPi 1 interface config file
    INTERFACE_FILE="rpi1.cfg"
    if [ "$RPI_VERSION" == "RPI2" ] || [ "$RPI_VERSION" == "RPI3" ]; then
        # use RPi 2 interface config file
        INTERFACE_FILE="rpi2.cfg"
    fi
    echo "Using interface file '$INTERFACE_FILE'"
    
    # flash the firmware
    sudo openocd -f interface/$INTERFACE_FILE -c "transport select swd; set CHIPNAME at91samd21j18; source [find target/at91samdXX.cfg]; adapter_khz 50; adapter_nsrst_delay 100; adapter_nsrst_assert_width 100" -c "init; targets; reset halt; program $FILE verify; reset" -c "shutdown"

else
    echo "Firmware file '$FILE' does not exist."
fi
