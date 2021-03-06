# BricKuber

This project is for a robot that solves a Rubik's cube, using LEGO Mindstorms and the [Dexter Industries BrickPi3.](https://www.dexterindustries.com/brickpi/)  

The project has been updated in March 2021 to bring it to Python3 as some of the dependencies are no longer available in Python2. It has not been fully tested unfortunately.



## Software
Install dependencies by running the install_brickuber.sh setup script:

    sudo bash ~/Dexter/BrickPi3/Projects/BricKuber/install_brickuber.sh

Enable the Raspberry Pi Camera:
 * Run `sudo raspi-config`
 * select `Interfacing Options`
 * select `Camera`
 * select `<Yes>`
 * hit enter and then the right arrow twice and then enter (which will select `<Finish>`)
 * when asked if you would like to reboot now, select `<yes>`

This project uses the following software packages installed by the install_brickuber.sh script:

* [rubiks-cube-tracker](https://github.com/dwalton76/rubiks-cube-tracker) for converting an image of a Rubik's cube face into a set of nine RGB values.
* [rubiks-color-resolver](https://github.com/dwalton76/rubiks-color-resolver) for converting 54 sets of RGB values into nine each of six unique colors.
* [kociemba](https://github.com/muodov/kociemba) for computing an efficient Rubik's cube solve solution.

## Hardware

* Build the robot according to the [MindCuber](http://mindcuber.com/) building instructions.
* Substitute the BrickPi3 and Raspberry Pi Camera for the Mindstorms brick, color sensor, and sensor assembly.
* Connect the turn-table motor to BrickPi3 port MA.
* Connect the grabber motor to BrickPi3 port MB.

## Tuning

Depending on any modifications you have made to the model, you may need to tune the following variables:
* `self.MOTOR_GRAB_POSITION_HOME      = 0 `	This is the start position of the grabber.
* `self.MOTOR_GRAB_POSITION_REST      = -35`  This is a middle position of the grabber.
* `self.MOTOR_GRAB_POSITION_FLIP_PUSH = -90`  This is a middle position of the grabber.
* `self.MOTOR_GRAB_POSITION_GRAB      = -130` This is a middle position of the grabber.
* `self.MOTOR_GRAB_POSITION_FLIP      = -240`	This is the fully extended position of the grabber.
