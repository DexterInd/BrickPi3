BrickPi3
========
The BrickPi3 connects LEGO Mindstorms with the Raspberry Pi.  You can learn [more about the BrickPi3 here.](https://www.dexterindustries.com/brickpi/)

![BrickPi3 Introduction Header](https://user-images.githubusercontent.com/29712567/32540756-0d9f7224-c487-11e7-9941-968fa33dd95a.png)

Documentation
-------------
You can find more extensive documentation about setting up the BrickPi3 for the first time, other programming languages contributed by our community, and more extensive information on our projects [on the Dexter Industries website here.](https://www.dexterindustries.com/brickpi3-tutorials-documentation/)

Installation
------------

Quick Install
-------------

In order to quickly install the `BrickPi3` repository, open up a terminal and type the following command:
```
git clone https://github.com/DexterInd/BrickPi3.git
cd BrickPi3/Install
source install_trixie.sh user
```
The same command can be used for updating the `BrickPi3` to the latest version.

Compatibility
-------------

The following Lego Sensor and Motors are supported:

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

Raspberry Pi Compatibility
--------------------------

The BrickPi3 is compatible with all models of the Raspberry Pi, including the Raspberry Pi 5.  The BrickPi3 uses the SPI interface to communicate with the Raspberry Pi, so any model of Raspberry Pi that has an SPI interface will work with the BrickPi3.  The best board to use with BrickPi is still the Raspberry Pi 3B+ as it is the least power hungry and has the best performance for the price.  The Raspberry Pi 4 and 5 are also compatible with the BrickPi3, but they have higher power requirements and may require additional cooling.

There are some caveats regarding the Raspberry Pi 5.
* The RPI5 power requirements exceed the power that the BrickPi3 can supply, so you may need to use a separate power supply for the RPI5. Our internal testing has shown that the RPI5 can be powered through the BrickPi3, but it is not recommended as we had some random power-down issues.
* The RPI5 often requires a fan to keep its temperature low but there is no space between the RPI and the BrickPi3 board to add a fan.
* The RPI5 can become quite hot, especially without a fan. It is not recommended to use the acrylic case with the RPI5 as it does not provide good ventilation.

License
-------

Please review the [LICENSE.md] file for license information.

[LICENSE.md]: ./LICENSE.md
