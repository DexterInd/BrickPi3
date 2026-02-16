# Program Name: simplebot_simple.py
# ================================
# This code is for moving the simplebot
# Author     Date      Comments
# Karan      04/11/13  Initial Authoring
# Nicole     2026/Feb/16   Updated for BrickPi3 and Python 3, added comments, and improved input handling with curses.
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
# Revised by T. Cooper 12/18
# --- program updated for Python 3
# --- curses interface added for consistent input mang.
# Commands:
#   w or UP arrow   - Move forward
#   a or LEFT arrow - Move left
#   d or RIGHT arrow- Move right
#   s or DOWN arrow - Move back
#   x               - Stop
# we add these libraries to give us the ability to use sleep func
# use Brick Pi 3 stuff and the curses interface (it makes input easier and consistent)

import time
import brickpi3  # import BrickPi3.py file to use BrickPi operations
try:
    import curses    # import curses for text processing
except ImportError:
    print("Error: The 'curses' module is required for this program.\n" \
          "On Raspberry Pi OS or Debian/Ubuntu, install it with:\n" \
          "    sudo apt-get install python3-curses\n")
    exit(1)

# set up curses interface
stdscr = curses.initscr()
curses.noecho()
stdscr.keypad(True)  # Enable special keys (like arrows)

instructions = [
    "Simplebot Control Instructions:",
    "  w or UP arrow     - Move forward",
    "  a or LEFT arrow   - Move left",
    "  d or RIGHT arrow  - Move right",
    "  s or DOWN arrow   - Move back",
    "  x or SPACE        - Stop",
    "Press Ctrl+C to exit."
]
for idx, line in enumerate(instructions):
    stdscr.addstr(idx, 0, line)
stdscr.refresh()

BP = brickpi3.BrickPi3()  # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.
motorR = BP.PORT_B  # right motor
motorL = BP.PORT_C  # left motor
speed = 200  # range is -255 to 255, make lower if bot is too fast

# Move Forward
def fwd():
    BP.set_motor_power(motorR, speed)
    BP.set_motor_power(motorL, speed)

# Move Left
def left():
    BP.set_motor_power(motorR, speed)
    BP.set_motor_power(motorL, -speed)

# Move Right
def right():
    BP.set_motor_power(motorR, -speed)
    BP.set_motor_power(motorL, speed)

# Move backward
def back():
    BP.set_motor_power(motorR, -speed)
    BP.set_motor_power(motorL, -speed)

# Stop
def stop():
    BP.set_motor_power(motorR, 0)
    BP.set_motor_power(motorL, 0)

try:
    while True:
        inp = stdscr.getkey()  # Take input from the terminal
        # Move the bot
        if inp == 'w' or inp == 'KEY_UP':
            fwd()
            stdscr.addstr(len(instructions)+1, 0, "fwd   ")
        elif inp == 'a' or inp == 'KEY_LEFT':
            left()
            stdscr.addstr(len(instructions)+1, 0, "left  ")
        elif inp == 'd' or inp == 'KEY_RIGHT':
            right()
            stdscr.addstr(len(instructions)+1, 0, "right ")
        elif inp == 's' or inp == 'KEY_DOWN':
            back()
            stdscr.addstr(len(instructions)+1, 0, "back  ")
        elif inp == 'x' or inp == ' ':  # Spacebar
            stop()
            stdscr.addstr(len(instructions)+1, 0, "stop  ")
        stdscr.refresh()
        time.sleep(0.01)  # sleep for 10 ms
except KeyboardInterrupt:
    stop()
    try:
        curses.endwin()
    except Exception:
        pass
    print("\nExiting and stopping motors.")
    exit(0)
except Exception as e:
    stop()
    try:
        curses.endwin()
    except Exception:
        pass
    print(f"\nError: {e}\nExiting and stopping motors.")
