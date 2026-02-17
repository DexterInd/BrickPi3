#! /bin/bash

PIHOME=$HOME
DEXTER=Dexter
DEXTER_PATH=$PIHOME/$DEXTER
RASPBIAN=$PIHOME/di_update/Raspbian_For_Robots
BRICKPI3_DIR=$DEXTER_PATH/BrickPi3
DEXTERSCRIPT=$DEXTER_PATH/lib/Dexter/script_tools

source $DEXTERSCRIPT/functions_library.sh

check_root_user() {
    if [[ $EUID -ne 0 ]]; then
        feedback "FAIL!  This script must be run as such: sudo ./install.sh"
        exit 1
    fi
}

install_dependencies() {

    # the sudo apt-get update is already
    # done by the script_tools installer in
    # update_brickpi3.sh

    feedback "No package dependencies for the BrickPi3"
    #feedback "Installing Dependencies for the BrickPi3"
    #feedback "Dependencies installed for the BrickPi3"
}

install_wiringpi() {
    # Check if WiringPi Installed

    # using curl piped to bash does not leave a file behind. no need to remove it
    # we can do either the curl - it works just fine
    # sudo curl https://raw.githubusercontent.com/DexterInd/script_tools/master/update_wiringpi.sh | bash
    # or call the version that's already on the SD card
    sudo bash $DEXTERSCRIPT/update_wiringpi.sh
    # done with WiringPi

    # remove wiringPi directory if present
    if [ -d wiringPi ]
    then
        sudo rm -r wiringPi
    fi
    # End check if WiringPi installed
}

enable_spi() {
    feedback "Removing blacklist from /etc/modprobe.d/raspi-blacklist.conf"

    if grep -q "#blacklist spi-bcm2708" /etc/modprobe.d/raspi-blacklist.conf; then
        echo "SPI already removed from blacklist"
    else
        sudo sed -i -e 's/blacklist spi-bcm2708/#blacklist spi-bcm2708/g' /etc/modprobe.d/raspi-blacklist.conf
        echo "SPI removed from blacklist"
    fi

    #Adding in /etc/modules
    feedback "Adding SPI-dev in /etc/modules"

    if grep -q "spi-dev" /etc/modules; then
        echo "spi-dev already there"
    else
        echo spi-dev >> /etc/modules
        echo "spi-dev added"
    fi
    feedback "Making SPI changes in /boot/config.txt"

    if grep -q "#dtparam=spi=on" /boot/config.txt; then
        sudo sed -i 's/#dtparam=spi=on/dtparam=spi=on/g' /boot/config.txt
        echo "SPI enabled"
    elif grep -q "dtparam=spi=on" /boot/config.txt; then
        echo "SPI already enabled"
    else
        sudo sh -c "echo 'dtparam=spi=on' >> /boot/config.txt"
        echo "SPI enabled"
    fi

}

check_root_user
install_dependencies
install_wiringpi
enable_spi
