#! /bin/bash

PIHOME=/home/pi
DEXTER=Dexter
DEXTER_PATH=$PIHOME/$DEXTER
RASPBIAN=$PIHOME/di_update/Raspbian_For_Robots
BRICKPI3_DIR=$DEXTER_PATH/BrickPi3
DEXTERSCRIPT=$DEXTER_PATH/lib/Dexter/script_tools

# the top-level module name of each package
# used for identifying present packages
REPO_PACKAGE=brickpi3

# the following option specifies which BrickPi3 github branch to use
selectedbranch="master"

##############################################
######## Parse Command Line Arguments ########
##############################################

# called way down bellow
check_if_run_with_pi() {
  ## if not running with the pi user then exit
  if [ $(id -ur) -ne $(id -ur pi) ]; then
    echo "BrickPi3 installer script must be run with \"pi\" user. Exiting."
    exit 7
  fi
}

# called way down bellow
parse_cmdline_arguments() {

    # whether to install the dependencies or not (apt-get etc.)
    installdependencies=true
    updaterepo=true
    install_pkg_scriptools=true

    # the following 3 options are mutually exclusive
    systemwide=true
    userlocal=false
    envlocal=false
    usepython3exec=true

    declare -ga optionslist=("--system-wide")
    # iterate through bash arguments
    for i; do
      case "$i" in
        --no-dependencies)
          installdependencies=false
          ;;
        --no-update-aptget)
          updaterepo=false
          ;;
        --bypass-pkg-scriptools)
          install_pkg_scriptools=false
          ;;
        --user-local)
          userlocal=true
          systemwide=false
          declare -ga optionslist=("--user-local")
          ;;
        --env-local)
          envlocal=true
          systemwide=false
          declare -ga optionslist=("--env-local")
          ;;
        --system-wide)
          ;;
        develop|feature/*|hotfix/*|fix/*|DexterOS*|v*)
          selectedbranch="$i"
          ;;
      esac
    done

    # show some feedback on the console
    if [ -f $DEXTERSCRIPT/functions_library.sh ]; then
      source $DEXTERSCRIPT/functions_library.sh
      # show some feedback for the BrickPi3
      if [ ! quiet_mode ]; then
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
        echo "  ____       _      _    ____  _ _____ "
        echo " | __ ) _ __(_) ___| | _|  _ \(_)___ / "
        echo " |  _ \| '__| |/ __| |/ / |_) | | |_ \ "
        echo " | |_) | |  | | (__|   <|  __/| |___) |"
        echo " |____/|_|  |_|\___|_|\_\_|   |_|____/ "
        echo "                                       "
      fi
      feedback "Welcome to BrickPi3 Installer."
    else
      echo "Welcome to BrickPi3 Installer."
    fi
    echo "Updating BrickPi3 for $selectedbranch branch with the following options:"
    ([[ $installdependencies = "true" ]] && echo "  --no-dependencies=false") || echo "  --no-dependencies=true"
    ([[ $updaterepo = "true" ]] && echo "  --no-update-aptget=false") || echo "  --no-update-aptget=true"
    ([[ $install_pkg_scriptools = "true" ]] && echo "  --bypass-pkg-scriptools=false") || echo "  --bypass-pkg-scriptools=true"
    echo "  --user-local=$userlocal"
    echo "  --env-local=$envlocal"
    echo "  --system-wide=$systemwide"

    # in case the following packages are not installed and `--no-dependencies` option has been used
    if [[ $installdependencies = "false" ]]; then
      command -v git >/dev/null 2>&1 || { echo "This script requires \"git\" but it's not installed. Exiting." >&2; exit 1; }
      command -v python >/dev/null 2>&1 || { echo "Executable \"python\" couldn't be found. Don't use --no-dependencies option. Exiting." >&2; exit 2; }
      command -v python3 >/dev/null 2>&1 || { echo "Executable \"python3\" couldn't be found. Don't use --no-dependencies option. Exiting." >&2; exit 3; }
      #command -v pip >/dev/null 2>&1 || { echo "Executable \"pip\" couldn't be found. Don't use --no-dependencies option. Exiting." >&2; exit 4; }
      #command -v pip3 >/dev/null 2>&1 || { echo "Executable \"pip3\" couldn't be found. Don't use --no-dependencies option. Exiting." >&2; exit 5; }
    fi

    # create rest of list of arguments for script_tools call
    optionslist+=("$selectedbranch")
    [[ $usepython3exec = "true" ]] && optionslist+=("--use-python3-exe-too")
    [[ $updaterepo = "true" ]] && optionslist+=("--update-aptget")
    [[ $installdependencies = "true" ]] && optionslist+=("--install-deb-deps")
    [[ $install_pkg_scriptools = "true" ]] && optionslist+=("--install-python-package")

    echo "Options used for script_tools script: \"${optionslist[@]}\""
}

######################################
######## Install Script_Tools ########
######################################
install_scriptools() {

  # update script_tools first
  rm -f $PIHOME/.tmp_script_tools.sh
  #curl --silent -kL dexterindustries.com/update_tools > $PIHOME/.tmp_script_tools.sh
  # MT use Robert's repo for developing
  curl --silent -kL https://raw.githubusercontent.com/RobertLucian/script_tools/feature/arg-based-installation/install_script_tools.sh > $PIHOME/.tmp_script_tools.sh

  echo "Installing script_tools with options: \"${optionslist[@]}\""
  bash $PIHOME/.tmp_script_tools.sh ${optionslist[@]} > /dev/null
  ret_val=$?
  rm $PIHOME/.tmp_script_tools.sh
  if [[ $ret_val -ne 0 ]]; then
    echo "script_tools failed installing with exit code $ret_val. Aborting."
    exit 6
  fi

  # needs to be sourced from here when we call this as a standalone
  source $DEXTERSCRIPT/functions_library.sh
}

################################################
######## Install Python Packages & Deps ########
################################################
clone_brickpi3() {

  echo "Installing BrickPi3 package."

  # create folders recursively if they don't exist already
  # we use sudo for creating the dir(s) because on older versions of R4R
  # the sudo command is used, and hence we need to be sure we have write permissions.
  sudo mkdir -p $DEXTER_PATH
  # still only available for the pi user
  # shortly after this, we'll make it work for any user
  sudo chown pi:pi -R $DEXTER_PATH
  cd $DEXTER_PATH

  # it's simpler and more reliable (for now) to just delete the repo and clone a new one
  # otherwise, we'd have to deal with all the intricacies of git

  sudo rm -rf $BRICKPI3_DIR
  # MT for testing temporarily use mattallen37 repo for cloning.
  #git clone --quiet --depth=1 -b $selectedbranch https://github.com/DexterInd/BrickPi3.git
  git clone --quiet --depth=1 -b feature/easy-python-installation https://github.com/mattallen37/BrickPi3.git
  cd $BRICKPI3_DIR
}

install_python_packages() {
  [[ $systemwide = "true" ]] && sudo python setup.py install \
              && [[ $usepython3exec = "true" ]] && sudo python3 setup.py install
  [[ $userlocal = "true" ]] && python setup.py install --user \
              && [[ $usepython3exec = "true" ]] && python3 setup.py install --user
  [[ $envlocal = "true" ]] && python setup.py install \
              && [[ $usepython3exec = "true" ]] && python3 setup.py install
}

remove_python_packages() {
  # the 1st and only argument
  # takes the name of the package that needs to removed
  rm -f $PIHOME/.pypaths

  # get absolute path to python package
  # saves output to file because we want to have the syntax highlight working
  # does this for both root and the current user because packages can be either system-wide or local
  # later on the strings used with the python command can be put in just one string that gets used repeatedly
  python -c "import pkgutil; import os; \
              eggs_loader = pkgutil.find_loader('$1'); found = eggs_loader is not None; \
              output = os.path.dirname(os.path.realpath(eggs_loader.get_filename('$1'))) if found else ''; print(output);" >> $PIHOME/.pypaths
  sudo python -c "import pkgutil; import os; \
              eggs_loader = pkgutil.find_loader('$1'); found = eggs_loader is not None; \
              output = os.path.dirname(os.path.realpath(eggs_loader.get_filename('$1'))) if found else ''; print(output);" >> $PIHOME/.pypaths
  if [[ $usepython3exec = "true" ]]; then
    python3 -c "import pkgutil; import os; \
                eggs_loader = pkgutil.find_loader('$1'); found = eggs_loader is not None; \
                output = os.path.dirname(os.path.realpath(eggs_loader.get_filename('$1'))) if found else ''; print(output);" >> $PIHOME/.pypaths
    sudo python3 -c "import pkgutil; import os; \
                eggs_loader = pkgutil.find_loader('$1'); found = eggs_loader is not None; \
                output = os.path.dirname(os.path.realpath(eggs_loader.get_filename('$1'))) if found else ''; print(output);" >> $PIHOME/.pypaths
  fi

  # removing eggs for $1 python package
  # ideally, easy-install.pth needs to be adjusted too
  # but pip seems to know how to handle missing packages, which is okay
  while read path;
  do
    if [ ! -z "${path}" -a "${path}" != " " ]; then
      echo "Removing ${path} egg"
      sudo rm -f "${path}"
    fi
  done < $PIHOME/.pypaths
}

install_python_pkgs_and_dependencies() {
  # installing dependencies if required
  if [[ $installdependencies = "true" ]]; then
    pushd $BRICKPI3_DIR/Install > /dev/null
    sudo bash ./install.sh
    popd > /dev/null
  fi

  feedback "Removing \"$REPO_PACKAGE\" to make space for the new one"
  remove_python_packages "$REPO_PACKAGE"

  # installing the package itself
  pushd $BRICKPI3_DIR/Software/Python > /dev/null
  install_python_packages
  popd > /dev/null

  # Install C++ drivers
  echo "Installing BrickPi3 C++ drivers"
  echo "Copying BrickPi3.h and BrickPi3.cpp to /usr/local/include"
  sudo rm -f /usr/local/include/BrickPi3.h
  sudo rm -f /usr/local/include/BrickPi3.cpp
  sudo cp $BRICKPI3_DIR/Software/C/BrickPi3.h /usr/local/include/BrickPi3.h
  sudo cp $BRICKPI3_DIR/Software/C/BrickPi3.cpp /usr/local/include/BrickPi3.cpp

  # install openocd
  echo "Installing OpenOCD for BrickPi3"
  curl --silent https://raw.githubusercontent.com/DexterInd/openocd/master/openocd_install.sh | bash
}

################################################
######## Call all functions - main part ########
################################################

check_if_run_with_pi
parse_cmdline_arguments "$@"
install_scriptools
clone_brickpi3
install_python_pkgs_and_dependencies

exit 0
