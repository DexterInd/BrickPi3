#! /bin/bash

if [[ $EUID -ne 0 ]]; then
	echo "This script must be run as root" 
	exit 1
fi

SCRIPTDIR="$(readlink -f $(dirname $0))"
echo $SCRIPTDIR

#check if there's an argument on the command line
if [[ -f /home/pi/quiet_mode ]]
then
	quiet_mode=1
else
	quiet_mode=0
fi

if [[ "$quiet_mode" -eq "0" ]]
then
	echo "  _____            _                                ";
	echo " |  __ \          | |                               ";
	echo " | |  | | _____  _| |_ ___ _ __                     ";
	echo " | |  | |/ _ \ \/ / __/ _ \ '__|                    ";
	echo " | |__| |  __/>  <| ||  __/ |                       ";
	echo " |_____/ \___/_/\_\\__\___|_| _        _            ";
	echo " |_   _|         | |         | |      (_)           ";
	echo "   | |  _ __   __| |_   _ ___| |_ _ __ _  ___  ___  ";
	echo "   | | | '_ \ / _\ | | | / __| __| '__| |/ _ \/ __| ";
	echo "  _| |_| | | | (_| | |_| \__ \ |_| |  | |  __/\__ \ ";
	echo " |_____|_| |_|\__,_|\__,_|___/\__|_|  |_|\___||___/ ";
	echo "                                                    ";
	echo "                                                    ";
    
    echo "  ____       _      _    ____  _ _____ ";
    echo " | __ ) _ __(_) ___| | _|  _ \(_)___ / ";
    echo " |  _ \| '__| |/ __| |/ / |_) | | |_ \ ";
    echo " | |_) | |  | | (__|   <|  __/| |___) |";
    echo " |____/|_|  |_|\___|_|\_\_|   |_|____/ ";
    echo "                                       ";
fi

echo "Welcome to BrickPi3 Installer.";

