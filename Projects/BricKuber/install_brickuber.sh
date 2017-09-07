#! /bin/bash

sudo apt-get update

# install rubiks-cube-tracker
sudo apt-get install python-pip python-opencv -y
sudo pip install git+https://github.com/dwalton76/rubiks-cube-tracker.git

# install rubiks-color-resolver
sudo pip3 install scikit-learn
sudo apt-get install python3-pip -y
sudo pip3 install git+https://github.com/dwalton76/rubiks-color-resolver.git

# install kociemba
sudo apt-get install libffi-dev -y
sudo pip install kociemba
