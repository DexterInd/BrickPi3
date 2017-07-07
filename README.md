BrickPi3
========
The BrickPi3 connects LEGO Mindstorms with the Raspberry Pi.


Installation
------------

On Raspbian for Robots, run DI Update to install or update to the latest version.

On Raspbian:

1. For install, clone this repository onto the Raspberry Pi:

        sudo git clone http://www.github.com/DexterInd/BrickPi3.git /home/pi/Dexter/BrickPi3

    For update, pull the repository:

        sudo git --work-tree=/home/pi/Dexter/BrickPi3 --git-dir=/home/pi/Dexter/BrickPi3/.git pull

2. Run the install script:

        sudo bash /home/pi/Dexter/BrickPi3/Install/install.sh

3. Reboot the Raspberry Pi to make the settings take effect:

        sudo reboot


Compatibility
-------------

The following Lego Sensor and Motors are supported by Python and Scratch:

* Lego Sensors
  * EV3
    * Ultrasonic Sensor
    * Gyro Sensor
    * Color Sensor
    * Touch Sensor
    * Infrared Sensor
  * NXT
    * Ultrasonic Sensor
    * Color Sensor
    * Light Sensor
    * Touch Sensor

* Lego Motors
  * EV3 Large Motor
  * EV3 Medium Motor
  * NXT Motor

In addition, the BrickPi3 firmware and Python drivers support custom analog and
I2C sensors. Most NXT and EV3 aftermarket sensors should work if you add custom
python support. See [this python example for reading custom analog sensors][ex1]
and [this python example for reading custom I2C sensors][ex2].

[ex1]: https://github.com/DexterInd/BrickPi3/blob/master/Software/Python/Examples/Analog_Sensor.py
[ex2]: https://github.com/DexterInd/BrickPi3/blob/master/Software/Python/Examples/DI-dTIR.py


License
-------

Please review the [LICENSE.md] file for license information.

[LICENSE.md]: ./LICENSE.md
