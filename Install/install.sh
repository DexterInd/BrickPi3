#! /bin/bash

# install script_tools
curl --silent https://raw.githubusercontent.com/DexterInd/script_tools/master/install_script_tools.sh | bash

# install openocd
curl --silent https://raw.githubusercontent.com/DexterInd/openocd/master/openocd_install.sh | bash

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root" 
    exit 1
fi

SCRIPTDIR="$(readlink -f $(dirname $0))"
echo $SCRIPTDIR
REPO_PATH=$(readlink -f $(dirname $0) | grep -E -o "^(.*?\\BrickPi3)")

#check if there's an argument on the command line
if [[ -f /home/pi/quiet_mode ]]
then
    quiet_mode=1
else
    quiet_mode=0
fi

if [[ "$quiet_mode" -eq "0" ]]
then
    echo "  _____            _                                "
    echo " |  __ \          | |                               "
    echo " | |  | | _____  _| |_ ___ _ __                     "
    echo " | |  | |/ _ \ \/ / __/ _ \ '__|                    "
    echo " | |__| |  __/>  <| ||  __/ |                       "
    echo " |_____/ \___/_/\_\ __\___|_| _        _            "
    echo " |_   _|         | |         | |      (_)           "
    echo "   | |  _ __   __| |_   _ ___| |_ _ __ _  ___  ___  "
    echo "   | | | '_ \ / _\ | | | / __| __| '__| |/ _ \/ __| "
    echo "  _| |_| | | | (_| | |_| \__ \ |_| |  | |  __/\__ \ "
    echo " |_____|_| |_|\__,_|\__,_|___/\__|_|  |_|\___||___/ "
    echo "                                                    "
    echo "                                                    "
fi

echo "  ____       _      _    ____  _ _____ "
echo " | __ ) _ __(_) ___| | _|  _ \(_)___ / "
echo " |  _ \| '__| |/ __| |/ / |_) | | |_ \ "
echo " | |_) | |  | | (__|   <|  __/| |___) |"
echo " |____/|_|  |_|\___|_|\_\_|   |_|____/ "
echo "                                       "

echo ""
echo "Welcome to BrickPi3 Installer."

# Adding in /etc/modules
echo ""
if grep -q "spi-dev" /etc/modules; then
    echo "spi-dev already present in /etc/modules"
else
    echo spi-dev >> /etc/modules
    echo "spi-dev added to /etc/modules"
fi

# Enable SPI
echo ""
if grep -q "#dtparam=spi=on" /boot/config.txt; then
    sudo sed -i 's/#dtparam=spi=on/dtparam=spi=on/g' /boot/config.txt
    echo "SPI enabled"
elif grep -q "dtparam=spi=on" /boot/config.txt; then
    echo "SPI already enabled"
else
    echo 'dtparam=spi=on' >> /boot/config.txt
    echo "SPI enabled"
fi

# Install python and python3 modules
echo ""
cd $REPO_PATH/Software/Python/
echo "Installing python modules"
echo ""
sudo python setup.py install
echo ""
echo "Installing python3 modules"
echo ""
sudo python3 setup.py install

# Install C++ drivers
echo ""
echo "Installing C++ drivers"
echo "Copying BrickPi3.h and BrickPi3.cpp to /usr/local/include"
cp $REPO_PATH/Software/C/BrickPi3.h /usr/local/include/BrickPi3.h
cp $REPO_PATH/Software/C/BrickPi3.cpp /usr/local/include/BrickPi3.cpp

# not the job of this script. It's being done in fetch_brickpi3
# and only for users who have the whole raspbian for robots
# standalone users do not need the softlink
# if [ ! -d /home/pi/Desktop/BrickPi3 ] 
# then
# 	echo "Putting BrickPi3 folder on the desktop"
#     sudo ln -s  /home/pi/Dexter/BrickPi3 /home/pi/Desktop/BrickPi3
# fi

echo ""
echo "Installation complete"
echo "Please reboot to make settings take effect"
