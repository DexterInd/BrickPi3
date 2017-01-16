To troubleshoot the BrickPi3
----------------------------
If the BrickPi3 is not performing as expected, here are some things to try:
* Check how fast the yellow LED is flashing. If it's flashing 1 time per second, the battery voltage is good (at least 7.2v). If it's flashing twice per second, the battery voltage is adequate, but not great (less than 7.2v). If it's flashing 4 times per second, the battery voltage is too low, and the motors are automatically disabled.
* Ensure adequate voltage for running the BrickPi3 and Raspberry Pi. If the battery voltage is below 6.8v, the motors might be automatically disabled in attempt to keep the Raspberry Pi from crashing due to dead batteries. If the battery voltage is below about 6.5v, the Raspberry Pi might not be getting adequate power. Instead of running on batteries, you can connect 5v directly to the Raspberry Pi using the micro-USB power input connector to ensure that the Raspberry Pi will be powered adequately in case your batteries are dead.
* Run the troubleshooting script "all_tests.sh". Look through the output to see if there's anything unexpected. If you don't find the problem, you can upload the log.txt file from the desktop (/home/pi/Desktop/log.txt) to the [forums](http://forum.dexterindustries.com/c/brickpi) and ask for help (please give a clear description of the problem you're experiencing). You can run the troubleshooting script by running this:

    `sudo bash /home/pi/Dexter/BrickPi3/Troubleshooting/all_tests.sh`
