#! /bin/bash

# Detect RPi version from device tree model string (no Python dependency)
MODEL=$(tr -d '\0' < /proc/device-tree/model 2>/dev/null || cat /proc/cpuinfo | grep -i "model name" | head -1)
echo "Detected model: $MODEL"

RPI_VERSION="unknown"
case "$MODEL" in
    *"Pi 5"*)   RPI_VERSION="RPI5" ;;
    *"Pi 4"*)   RPI_VERSION="RPI4" ;;
    *"Pi 3"*)   RPI_VERSION="RPI3" ;;
    *"Pi 2"*)   RPI_VERSION="RPI2" ;;
    *"Pi Zero"*) RPI_VERSION="RPI0" ;;
    *"Pi 1"*|*"Model A"*|*"Model B"*) RPI_VERSION="RPI1" ;;
esac

echo "Found $RPI_VERSION"

INTERFACE_FILE="none"
if [ "$RPI_VERSION" == "RPI1" ] || [ "$RPI_VERSION" == "RPI0" ] || \
   [ "$RPI_VERSION" == "RPI2" ] || [ "$RPI_VERSION" == "RPI3" ] || \
   [ "$RPI_VERSION" == "RPI4" ]; then
    INTERFACE_FILE="raspberrypi-native.cfg"
elif [ "$RPI_VERSION" == "RPI5" ]; then
    INTERFACE_FILE="RPI5_INLINE"
fi

if [ "$INTERFACE_FILE" == "none" ]; then
    # unsupported RPI
    echo "Unsupported RPi version '$RPI_VERSION'. Please report to support@dexterindustries.com"
else
    # Ensure openocd is installed
    if ! command -v openocd &>/dev/null; then
        echo "openocd not found. Installing..."
        sudo apt-get update -qq && sudo apt-get install -y openocd
        if ! command -v openocd &>/dev/null; then
            echo "ERROR: Failed to install openocd. Please install it manually: sudo apt-get install openocd"
            exit 1
        fi
    fi

    # Read the path of the BrickPi3 repository
    REPO_PATH=$(readlink -f $(dirname $0) | grep -E -o "^(.*?\\BrickPi3)")

    # Get the absolute path of the latest Firmware update (newest .bin if multiple exist)
    FIRMWARE_FILE=$(sudo find "$REPO_PATH"/Firmware/ -maxdepth 1 -name "*.bin" -printf "%T@ %p\n" | sort -n | tail -1 | cut -d' ' -f2-)

    if [ -z "$FIRMWARE_FILE" ]; then
        echo "Failed to find firmware file."
    else
        echo "** Updating the BrickPi3 Firmware with '$FIRMWARE_FILE'"

        if [ "$INTERFACE_FILE" == "RPI5_INLINE" ]; then
            # RPi5 uses the linuxgpiod driver with explicit GPIO numbers (schematic: SWCLK=GPIO25, SWDIO=GPIO24).
            # The spi_dw kernel driver claims GPIO 8 (SPI CS0); unload it so OpenOCD can claim the SWD lines cleanly.
            echo "RPi5: setting PCIe performance mode and freeing SPI GPIO lines..."
            echo performance | sudo tee /sys/module/pcie_aspm/parameters/policy > /dev/null
            sudo modprobe -r spidev spi_dw_mmio spi_dw 2>/dev/null || true

            sudo openocd \
              -c "adapter driver linuxgpiod" \
              -c "adapter gpio swclk -chip 0 25" \
              -c "adapter gpio swdio -chip 0 24" \
              -c "transport select swd" \
              -c "adapter speed 50" \
              -c "set CHIPNAME at91samd21j18; source [find target/at91samdXX.cfg]" \
              -c "init; reset halt; program $FIRMWARE_FILE verify; reset" \
              -c "shutdown"

            # Restore SPI so the BrickPi3 Python library can communicate normally
            sudo modprobe spi_dw spi_dw_mmio spidev 2>/dev/null || true
        else
            echo "Using interface file '$INTERFACE_FILE' for RPi version '$RPI_VERSION'."
            sudo openocd \
              -f interface/$INTERFACE_FILE \
              -c "adapter gpio swclk 25" \
              -c "adapter gpio swdio 24" \
              -c "transport select swd" \
              -c "adapter speed 50" \
              -c "adapter srst delay 100" \
              -c "adapter srst pulse_width 100" \
              -c "set CHIPNAME at91samd21j18; source [find target/at91samdXX.cfg]" \
              -c "init; targets; reset halt; program $FIRMWARE_FILE verify; reset" \
              -c "shutdown"
        fi

        echo
        echo 'if you see ** Verified OK ** then all is good. If not, please try again. Sometimes it can take a few tries before it works.'
    fi
fi
