BrickPi3
========
The BrickPi3 connects LEGO Mindstorms with the Raspberry Pi.  You can learn [more about the BrickPi3 here.](https://www.dexterindustries.com/brickpi/)  

![BrickPi3 Introduction Header](https://user-images.githubusercontent.com/29712567/32540756-0d9f7224-c487-11e7-9941-968fa33dd95a.png)

Documentation
-------------
You can find more extensive documentation about setting up the BrickPi3 for the first time, other programming languages contributed by our community, and more extensive information on our projects [on the Dexter Industries website here.](https://www.dexterindustries.com/brickpi3-tutorials-documentation/)

Installation
------------

On Raspbian for Robots, run `DI Software Update` to install or update - this is a more time-consuming option than the alternative instructions seen in the following section.

Quick Install
-------------

In order to quickly install the `BrickPi3` repository, open up a terminal and type the following command:
```
curl -kL dexterindustries.com/update_brickpi3 | bash
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

![BrickPi3 Introduction Header](https://user-images.githubusercontent.com/29712567/32540754-0d719912-c487-11e7-876c-06e311d1f2a5.jpg)


License
-------

Please review the [LICENSE.md] file for license information.

[LICENSE.md]: ./LICENSE.md
