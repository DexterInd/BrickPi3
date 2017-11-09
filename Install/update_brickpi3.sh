# Check for a BrickPi directory under "Dexter" folder.  If it doesn't exist, create it.
PIHOME=/home/pi
DEXTER=Dexter
DEXTER_PATH=$PIHOME/$DEXTER
RASPBIAN=$PIHOME/di_update/Raspbian_For_Robots
curl --silent https://raw.githubusercontent.com/DexterInd/script_tools/master/install_script_tools.sh | bash

# needs to be sourced from here when we call this as a standalone
source /home/pi/$DEXTER/lib/$DEXTER/script_tools/functions_library.sh

BRICKPI3_DIR=$DEXTER_PATH/BrickPi3
if folder_exists "$BRICKPI3_DIR" ; then
    echo "BrickPi3 Directory Exists"
    cd $DEXTER_PATH/BrickPi3    # Go to directory
    sudo git fetch origin       # Hard reset the git files
    sudo git reset --hard  
    sudo git merge origin/master
    # change_branch $BRANCH
else
    cd $DEXTER_PATH
    git clone https://github.com/DexterInd/BrickPi3
    cd BrickPi3
    # change_branch $BRANCH  # change to a branch we're working on, if we've defined the branch above.
fi

sudo bash /home/pi/Dexter/BrickPi3/Install/install.sh
