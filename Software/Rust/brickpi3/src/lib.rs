
extern crate spidev;

#[allow(dead_code)]

mod brickpi3 {

use std::io;
use std::path::Path;
use spidev::{Spidev, SpidevOptions, SpidevTransfer, SPI_MODE_0};



pub struct BrickPi3 {
	spidev : Spidev,
}

impl BrickPi3 {
    /// Open the BrickPi3 device with the provided SPI device path
    ///
    /// Typically, the path will be something like `"/dev/spidev0.1"`
    pub fn open<P: AsRef<Path>>(path: P) -> io::Result<BrickPi3> {
    	let mut spi = try!(Spidev::open(path));
    	let options = SpidevOptions::new()
        		.bits_per_word(8)
         		.max_speed_hz(500_000)
         		.mode(SPI_MODE_0)
         		.build();
    	try!(spi.configure(&options));
    	Ok( BrickPi3{spidev: spi } )
    }


}

#[derive(Debug)]
#[derive(Clone)]   
#[derive(Copy)] 
#[allow(dead_code)]  
enum BPSPIMessage {
	None,

	GetManufacturer,      // 1
	GetName,
	GetHardwareVersion,
	GetFirmwareVersion,
	GetId,
	SetLed,
	GetVoltage3v3,
	GetVoltage5v,
	GetVoltage9v,
	GetVoltageVcc,
	SetAddress,           // 11

	SetSensorType,       // 12

	GetSensor1,          // 13
	GetSensor2,
	GetSensor3,
	GetSensor4,

	I2cTransact1,        // 17
	I2cTransact2,
	I2cTransact3,
	I2cTransact4,

	SetMotorPower,

	SetMotorPosition,

	SetMotorPositionKp,  

	SetMotorPositionKd, // 24

	SetMotorDps,         // 25

	SetMotorDpsKp,

	SetMotorDpsKd,

	SetMotorLimits,

	OffsetMotorEncoder,  // 29 

	GetMotorAEncoder,   // 30
	GetMotorBEncoder,
	GetMotorCEncoder,
	GetMotorDEncoder,

	GetMotorAStatus,    // 34
	GetMotorBStatus,
	GetMotorCStatus,
	GetMotorDStatus

 	}

}
