# BrickPi3 for .NET Core IoT

You will find a full implantation of BrickPi3 on [.NET Core IoT repository](https://github.com/dotnet/iot/). You will be able to program GoPiGo using C#. The full documentation and example is located into the main repository.

.NET Core is open source. .NET Core is best thought of as 'agile .NET'. Generally speaking it is the same as the Desktop .NET Framework distributed as part of the Windows operating system, but it is a cross platform (Windows, Linux, macOS) and cross architecture (x86, x64, ARM) subset that can be deployed as part of the application (if desired), and thus can be updated quickly to fix bugs or add features. It is a perfect fit for boards like Raspberry running Raspbian. Check the [.NET Core IoT documentation](https://github.com/dotnet/iot/tree/master/Documentation) if you are not familiar with .NET Core.

You will find below the general usage and extract of the full documentation. The .NET Core IoT implementation propose 2 ways to access BrickPi3: either thru a native drive either thru high level classes. In both cases, you need first to instantiate a BrickPi3 class.

Note: if you are interested in a Universal Windows Platform for Windows IoT Core for BrickPi3, you will find one [here](https://github.com/ellerbach/brickpi3). 

# How to use the driver

The main [BrickPi3.samples](https://github.com/dotnet/iot/tree/master/src/devices/BrickPi3) contains a series of test showing how to use every elements of the driver.

Create a ```Brick``` class.

```csharp
Brick brick = new Brick();
// Do whatever you want, read sensors, set motors, etc
// once finished, and class will be disposed, all motors will be floated and sensors reinitialized
```

If you have multiple BrickPi3 and want to change the address of a specific BrickPi3, use the ```SetAddress``` function. Be aware that once changed in the firmware it stays. By default the address 1.

Once you've done that, create, you can create a new brick by passing this address to the constructor. In this example, it will create a BrickPi3 with address 2.

If you want to use BrickPi3 on another board than the RaspberryPi and you have to change the defauklt SPI bus and chip select line, you can do it as well in the constructor. Please note that for Raspbarry Pi, the default is 0 for bus Id and 1 for chip select line.

```csharp
Brick brick = new Brick(2);
```

### Using sensors thru low level driver

To setup a sensor, you need first to set the type of sensor then you can read the data. The below example setup an NXT Touch sensor on port 1 and read the results in continue.

```csharp
Console.WriteLine("Running 100 reads on EV3 touch sensor on port 1.");
EV3TouchSensor touch = new EV3TouchSensor(brick, BrickPortSensor.PortS1);
// Alternative to test NXT touch sensor
// NXTTouchSensor touch = new NXTTouchSensor(brick, BrickPortSensor.PORT_S2);
int count = 0;
while (count < 100)
{
    Console.WriteLine(string.Format("NXT Touch, IsPRessed: {0}, ReadAsString: {1}, Selected mode: {2}",
        touch.IsPressed(), touch.ReadAsString(), touch.SelectedMode()));
    Task.Delay(300).Wait(); ;
}
```

Please note that the function ```Brick.GetSensor``` returns an array of byte, it's up to you to interpret correctly the data out of this function. Please read the [documentation](https://www.dexterindustries.com/BrickPi/brickpi3-technical-design-details/brickpi3-communication-protocol/) to have the full details of what every sensor return.

It is **strongly recommended** to use the high level classes implementing the logic to decode correctly the raw values of sensor like in the previous example. 

### Using motors thru low level driver

There are many ways you can use motors, either by setting the power, either by reading the encoder, either by setting a degree per second speed. Those 3 examples will show you how to use each of them.

#### Making a motor moving depending on the position of another motor

In this example, the motor on port D is used to set the position of the motor A. A simple NXT touch sensor is used to end the sequence when it is pressed.

You can see as well the MotorStatus classes containing all information on the motor. Flags are useful to understand if you have issues with the power or an overload of the motors. 

To reinitialize the encoder, simply set the offset to the current version like shown in the first 2 lines.

```csharp
brick.OffsetMotorEncoder((byte)MotorPort.PortD, brick.GetMotorEncoder((byte)MotorPort.PortD));
brick.OffsetMotorEncoder((byte)MotorPort.PortA, brick.GetMotorEncoder((byte)MotorPort.PortA));
brick.SetMotorPositionKD((byte)MotorPort.PortA);
brick.SetMotorPositionKP((byte)MotorPort.PortA);
// Float motor D
brick.SetMotorPower((byte)MotorPort.PortD, (byte)MotorSpeed.Float);
// set some limits
brick.SetMotorLimits((byte)MotorPort.PortA, 50, 200);
brick.SetSensorType((byte)SensorPort.Port1, SensorType.EV3Touch);
Console.WriteLine("Read Motor A and D positions. Press EV3 Touch sensor on port 1 to stop.");
//run until we press the button on port2
while (brick.GetSensor((byte)SensorPort.Port1)[0] == 0)
{
    var target = brick.GetMotorEncoder((byte)MotorPort.PortD);
    brick.SetMotorPosition((byte)MotorPort.PortA, target);
    var status = brick.GetMotorStatus((byte)MotorPort.PortA);
    Console.WriteLine($"Motor A Target Degrees Per Second: {target}; Motor A speed: {status.Speed}; DPS: {status.Dps}; Encoder: {status.Encoder}; Flags: {status.Flags}");
    Thread.Sleep(20);
}
```

Please note that this example uses directly the low level functions available on the Brick class.

## How to use the high level classes

There are high level classes to handle directly objects like NXT Touch sensors or EV3 Color sensor. There is as well a Motor  and a Vehicle class to make it easier to pilot and control the motors rather than thru the low level driver.

### Using the Sensor classes

Using the sensor classes is straight forward. Just reference a class and initialized it. Access properties and function. The ```ReadRaw()```, ```ReadAsString()``` functions are common to all sensors, ```Value``` and ```ValueAsString``` properties as well. 
A changed property event on the properties is raised with a minimum period you can determined when creating the class (or later).

Example creating a NXT Touch Sensor on port S2:

```csharp
Brick brick = new Brick();

NXTTouchSensor touch = new NXTTouchSensor(brick, BrickPortSensor.PortS2);
Console.WriteLine($"NXT Touch, Raw: {touch.ReadRaw()}, ReadASString: {touch.ReadAsString()}, IsPressed: {touch.IsPressed()}, NumberNodes: {touch.NumberOfModes()}, SensorName: {touch.GetSensorName()}");
```

Example of creating an EV3 Touch sensor on port S1 and will tell it to check changes in properties every 20 milliseconds.

```csharp
EV3TouchSensor ev3Touch = new EV3TouchSensor(brick, BrickPortSensor.PortS1, 20);
```

This allow to have as many sensors as you want as well as having multiple BrickPi3. Just pass to the sensor the Brick class and you're good to go.

All sensors will return a ```int.MaxValue``` in case of error when reading the data. Test the value when using it. This choice is to avoid having exceptions to handle when using those high level classes.

### Using Motors

Motors are as well really easy to use. You have functions ```Start()```, ```Stop()```, ```SetSpeed(speed) ``` and ```GetSpeed()``` which as you can expect will start, stop, change the speed and give you the current speed. A speed property is available as well and will change the speed. 

Lego motors have an encoder which gives you the position in 0.5 degree precision. You can get access thru function ```GetTachoCount()```. As the numbers can get big quite fast, you can reset this counter by using ```SetTachoCount(newnumber) ```. A ```TachoCount``` property is available as well. This property like for sensors can raise an event on a minimum time base you can setup.

```csharp
Brick brick = new Brick();

Motor motor = new Motor(brick, BrickPortMotor.PORT_D);
motor.SetSpeed(100); //speed goes from -100 to +100, others will float the motor
motor.Start();
motor.SetSpeed(motor.GetSpeed() + 10);
Console.WriteLine($"Encoder: {motor.GetTachoCount()}");
Console.WriteLine($"Encoder: {motor.TachoCount}"); //same as previous line
Console.WriteLine($"Speed: {motor.GetSpeed()}");
Console.WriteLine($"Speed: {motor.Speed}"); //same as previous line
motor.SetPolarity(Polarity.OppositeDirection); // change the direction
motor.Stop();
```

Here is an example of the ```Vehicle``` class: 

```csharp
Console.WriteLine("Vehicle drive test using Motor A for left, Motor D for right, not inverted direction");
Vehicle veh = new Vehicle(brick, BrickPortMotor.PortA, BrickPortMotor.PortD);
veh.DirectionOpposite = true;
Console.WriteLine("Driving backward");
veh.Backward(30, 5000);
Console.WriteLine("Driving forward");
veh.Foreward(30, 5000);
Console.WriteLine("Turning left");
veh.TrunLeftTime(30, 5000);
Console.WriteLine("Turning right");
veh.TrunRightTime(30, 5000);
Console.WriteLine("Turning left");
veh.TurnLeft(30, 180);
Console.WriteLine("Turning right");
veh.TurnRight(30, 180);
```

The ```Vehicle``` class offers functions with timeout allowing to drive for a certain amount of time. All timing are in milliseconds. Turning functions offers as well a degree mode which allows to turn by a certain degree rather than a specific time.
