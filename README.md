BrickPi3
========
The BrickPi3 connects LEGO Mindstorms with the Raspberry Pi.


Installation
------------

On Raspbian for Robots, run `DI Software Update` to install or update - this is a more time-consuming option than the alternative instructions seen in the following section.

Quick Install
-------------

In order to quick install the `BrickPi3` repository, open up a terminal and type the following command:
```
sudo curl -kL dexterindustries.com/update_brickpi3 | bash
```
The same command can be used for updating the `BrickPi3` to the latest version.

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
