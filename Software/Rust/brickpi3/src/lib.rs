
extern crate spidev;

#[allow(dead_code)]

mod brickpi3 {

use std::io;
use std::path::Path;
use spidev::{Spidev, SpidevOptions, SpidevTransfer, SPI_MODE_0};


const LONGEST_SPI_TRANSFER: usize = 29;

pub struct BrickPi3 {
	spidev : Spidev,
	txbuf : [u8;LONGEST_SPI_TRANSFER],
	rxbuf : [u8;LONGEST_SPI_TRANSFER],
}

// Result of device detection
pub struct Ident {
	manufacturer : String,
	board : String,
	firmware : String,
}


pub enum IdentError {
	WrongResponse,
	WrongDevice,
	FirmwareVersionMismatch,
}

pub enum SPIError {
	BadResponse,
	IOError(io::Error),
}

impl From<io::Error> for SPIError {
    fn from(e: io::Error) -> SPIError {
        SPIError::IOError(e)
    }
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

    	Ok( BrickPi3 {spidev: spi 
    				 , txbuf: [0;LONGEST_SPI_TRANSFER]
    				 , rxbuf: [0;LONGEST_SPI_TRANSFER]} )
    }

    pub fn detect(&self) -> Result<Ident,IdentError> {
    	Err(IdentError::WrongResponse)
    }


    fn spi_read_string(&mut self, msg_type: BPSPIMessage , size: usize) 
    -> Result<Vec<u8>,SPIError> {
    	self.txbuf[0] = 1;
    	self.txbuf[1] = msg_type as u8;
    	{
			let mut transfer = SpidevTransfer
					::read_write(&self.txbuf[0..(size-1)], &mut self.rxbuf[0..(size-1)]);
        	try!(self.spidev.transfer(&mut transfer));
    	}
        if self.rxbuf[3] != 0xA5 {
        	Err(SPIError::BadResponse)
        } else {
        	Ok( Vec::<u8>::from(& self.rxbuf[4..(size-1)]) )
        }

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
