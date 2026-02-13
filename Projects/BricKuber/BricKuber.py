#!/usr/bin/env python3
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2026 Modular Robotics Inc
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is for a Rubik's cube solving robot.
#
# Setup: Follow the instructions in the project's README.
#
# Results: Place an unsolved Rubik's cube into the solver, and run this program.
#     The robot will turn the cube to each face and the camera will take pictures.
#     The Raspberry Pi will use rubiks-cube-tracker and rubiks-color-resolver to
#     determine the cube configuration from the six pictures. The cube configuration
#     will get passed to kociemba to find an efficient solution. Once a solution is
#     generated, the robot will execute the moves to solve the Rubik's cube.

import time          # import the time library for the sleep function
import brickuber_lib # Rubik's cube move and read
import kociemba      # Rubik's cube solver

# Use this line if using the NXT1 mindcuber design
# RobotStyle = "NXT1"

# Use this line if using the EV3 mindcuber design
RobotStyle = "EV3"

# Print debug information?
PrintDebugInfo = True

Cuber = brickuber_lib.BricKuberLib(RobotStyle, PrintDebugInfo)

try:
    # Use camera to get cube colors, and return configuration string.
    if PrintDebugInfo:
        print("Taking pictures of each face, and determining cube configuration.")
    UnsolvedString = Cuber.ReadCubeColors()
    if PrintDebugInfo:
        print(UnsolvedString)

    # This produces a Kociemba string.  It should have 54 letters
    # Use kociemba to solve the cube based on the configuration string.
    if PrintDebugInfo:
        print("Using kociemba to compute an efficient solve solution.")
    SolutionCmds = kociemba.solve(UnsolvedString)
    if PrintDebugInfo:
        print(SolutionCmds)

    # Execute the moves to solve the cube.
    if PrintDebugInfo:
        print("Executing the solve solution.")
    Cuber.Moves(SolutionCmds)

    if PrintDebugInfo:
        print("Rubik's cube solved!")

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    Cuber.BP.reset_all()
except Exception as e:
    print("Error: " + str(e))

# Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
Cuber.BP.reset_all()
