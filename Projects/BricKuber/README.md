BricKuber
=
This project is for a robot that solves a Rubik's cube.

Software
-
Install dependencies by running the install_brickuber.sh setup script:

    sudo bash ~/Dexter/BrickPi3/Projects/BricKuber/install_brickuber.sh

This project uses the following software packages installed by the install_brickuber.sh script:

* [rubiks-cube-tracker](https://github.com/dwalton76/rubiks-cube-tracker) for converting an image of a Rubik's cube face into a set of nine RGB values.
* [rubiks-color-resolver](https://github.com/dwalton76/rubiks-color-resolver) for converting 54 sets of RGB values into nine each of six unique colors.
* [kociemba](https://github.com/muodov/kociemba) for computing an efficient Rubik's cube solve solution.

Hardware
-
* Build the robot according to the [MindCuber](http://mindcuber.com/) building instructions.
* Substitute the BrickPi3 and Raspberry Pi Camera for the Mindstorms brick, color sensor, and sensor assembly.
* Connect the turn-table motor to BrickPi3 port MA.
* Connect the grabber motor to BrickPi3 port MD.
