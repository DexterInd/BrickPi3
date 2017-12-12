//
// Rust drivers for the BrickPi3
//
// Copyright (C) 2017 Juhana Helovuo <juhe@iki.fi>
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
//
// BrickPi3 is an I/O board for Raspberry Pi made by Dexter Industries
//

extern crate spidev;
extern crate strum; // strum is for iterating over enums
#[macro_use] extern crate strum_macros;
#[macro_use] extern crate bitflags;



use std::io;
use std::ops::{Shl,Shr};
use std::path::Path;

use spidev::{Spidev, SpidevOptions, SpidevTransfer, SPI_MODE_0};

use strum::IntoEnumIterator;

const LONGEST_SPI_TRANSFER: usize = 29;
const BRICKPI3_ADDRESS: u8 = 1;

#[derive(Debug)]
#[derive(Clone)]   
#[derive(Copy)]
#[derive(PartialEq)] 
#[derive(Eq)]
// This is a list of sensor type codes known by the firmware
pub enum SensorType {
  None = 1, // Not configured for any sensor type
  I2c,
  Custom,   // Choose 9v pullup, pin 5 and 6 configuration, 
            // and what to read back (ADC 1 and/or ADC 6 (always reports digital 5 and 6)).
  
  Touch,    // Touch sensor. When this mode is selected, 
            // automatically configure for NXT/EV3 as necessary.
  TouchNxt,
  TouchEv3, // 6
  
  NxtLightOn, // 7
  NxtLightOff, 
  
  NxtColorRed, // 9
  NxtColorGreen,
  NxtColorBlue,
  NxtColorFull,
  NxtColorOff,
  
  NxtUltrasonic, // 14
  
  Ev3GyroAbs, // 15
  Ev3GyroDps,
  Ev3GyroAbsDps,
  
  Ev3ColorReflected, // 18
  Ev3ColorAmbient,
  Ev3ColorColor,
  Ev3ColorRawReflected,
  Ev3ColorColorComponents,
  
  Ev3UltrasonicCm, // 23
  Ev3UltrasonicInches,
  Ev3UltrasonicListen,
  
  Ev3InfraredProximity, // 26
  Ev3InfraredSeek,
  Ev3InfraredRemote 
}

#[derive(Debug)]
pub enum SensorData {
    I2c, // TODO i2c
    Custom { adc1: u16 , adc6: u16 , pin5: bool , pin6: bool },
    Touch { pressed: bool },
    LightReflected { brightness: u16 },
    LightAmbient { brightness: u16 },
    Color { color: i8, red: i16, green: i16, blue: i16, ambient: i16 },
    UltrasonicDistance { meters: f32 },
    UltrasonicPresence { presence: bool },
    Gyro { abs: i16, dps: i16 },
    InfraredProximity { proximity: u8 },
    InfraredSeek { distance: Vec<i8>, heading: Vec<i8> },
    InfraredRemote { remote: Vec<RemoteButtons> },
}

#[derive(Debug)]
pub enum SensorError {
  NotConfigured,
  Configuring,
  NoData,
  I2cError,        // Such as no ACK, SCL stretched too long, etc.  
  TypeMismatch,
  SPIError ( SPIError ),
  NotImplemented,
  UnknownStatusReported( u8 ),
}

impl From<SPIError> for SensorError {
    fn from(spie: SPIError) -> SensorError { SensorError::SPIError(spie) }
}

bitflags! {
    pub struct RemoteButtons: u8 {
        const RED_UP     = 0x01;
        const RED_DOWN   = 0x02;
        const BLUE_UP    = 0x04;
        const BLUE_DOWN  = 0x08;
        const BROADCAST = 0x10;
    }
}

pub enum SensorConfigFlags {
  I2cMidClock = 0x0001, // I2C. Send a clock pulse between reading and writing. Required by the NXT US sensor.
  Pin1Pull    = 0x0002, // I2C or custom. Enable 9v pullup on pin 1
  I2cRepeat   = 0x0004, // I2C. Keep performing the same transaction e.g. keep polling a sensor
  Pin5Dir     = 0x0010, // Custom. Set pin 5 output
  Pin5State   = 0x0020, // Custom. Set pin 5 high
  Pin6Dir     = 0x0100, // Custom. Set pin 6 output
  Pin6State   = 0x0200, // Custom. Set pin 6 high
  Report1Adc  = 0x1000, // Custom. Read pin 1 ADC
  Report6Adc  = 0x4000  // Custom. Read pin 6 ADC
}


#[derive(Debug)]
#[derive(Clone)]   
#[derive(Copy)] 
#[allow(dead_code)]  
enum GetStringCmd {
    GetManufacturer = 1,      // 1
    GetName = 2,
    GetId = 5,
}

pub enum GetVersionCmd {
    GetHardwareVersion = 3,
    GetFirmwareVersion = 4, 
}

pub enum GetVoltageCmd {
    Volt3v3 = 7,
    Volt5v = 8,
    Volt9v = 9,
    VoltBattery = 10,
}

#[allow(dead_code)]  
enum SendArrayCmd {
    SetSensorType = 12,
    SetMotorPower = 21,
    SetMotorPosition = 22,
    SetMotorDps = 25,
    SetMotorLimits = 28,
    OffsetMotorEncoder = 29,
}

#[allow(dead_code)]  
enum SendReadArrayCmd {
    GetSensor1 = 13,          // 13
    GetSensor2 = 14,
    GetSensor3 = 15,
    GetSensor4 = 16,
    GetMotorAStatus = 34,    // 34
    GetMotorBStatus = 35,
    GetMotorCStatus = 36,
    GetMotorDStatus = 37,
}

enum ReadU32Cmd {
    GetFirmwareVersion = 4,
    GetMotorAEncoder = 30,
    GetMotorBEncoder = 31,
    GetMotorCEncoder = 32,
    GetMotorDEncoder = 33,
}

enum WriteU8Cmd {
    SetLed = 6
}

#[derive(Debug)]
#[derive(Clone)]   
#[derive(Copy)] 
#[derive(EnumIter)] 
pub enum SensorPort {
    Port1, Port2, Port3, Port4,
}

impl SensorPort {
    fn as_bitfield(self) -> u8 {
        1 << (self as i32)
    }
}

#[derive(Debug)]
#[derive(Clone)]   
#[derive(Copy)]
#[derive(EnumIter)] 
pub enum MotorPort {
    PortA, PortB, PortC, PortD
}

pub const MOTOR_FLOAT : i8 = -128;
pub const LED_TO_FIRMWARE_CONTROL : u8 = 0xFF;
impl MotorPort {
    fn as_bitfield(self) -> u8 {
        1 << (self as i32)
    }
}

pub struct MotorStatus {
    pub state: u8, // how to interpret this?
    pub power: i8,
    pub position: i32,
    pub dps: i16
}



// Result of device detection
#[derive(Debug)]
pub struct Ident {
    pub manufacturer : String,
    pub board : String,
    pub firmware : u32,
}

#[allow(non_snake_case)]
pub fn version_as_String(ver: u32) -> String {
    format!("{}.{}.{}", ver / 1000000, (ver / 1000) % 1000, ver % 1000 )
}


#[derive(Debug)]
pub enum SPIError {
    BadResponse,
    TooLongSPITransfer,
    IOError(io::Error),
}

impl From<io::Error> for SPIError {
    fn from(e: io::Error) -> SPIError {
        SPIError::IOError(e)
    }
}

// ------------------------------------------------

pub struct BrickPi3 {
    spidev: Spidev,
    address: u8, // BrickPi3 SPI address, default = 1
    sensor_type: [SensorType ; 4],  
    //i2c_recv_count: [usize ; 4],
    txbuf : [u8 ; LONGEST_SPI_TRANSFER],
    rxbuf : [u8 ; LONGEST_SPI_TRANSFER],
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

        Ok( BrickPi3 { spidev: spi
                     , sensor_type: [SensorType::None ; 4]
                     //, i2c_recv_count: [ 0 ; 4] 
                     , address: BRICKPI3_ADDRESS // TODO: Allow changing this  
                     , txbuf: [0 ; LONGEST_SPI_TRANSFER]
                     , rxbuf: [0 ; LONGEST_SPI_TRANSFER]
                     } )
    }

    pub fn detect(&mut self) -> Result<Ident,SPIError> {
        let f = self.spi_read_32(ReadU32Cmd::GetFirmwareVersion) ?;
        let m = self.spi_read_vec(GetStringCmd::GetManufacturer , 20) ?;
        let b = self.spi_read_vec(GetStringCmd::GetName , 20) ?;
        // We are here ignoring the possibility that BrickPi3 returns a string
        // that may not be valid UTF-8.
        Ok( Ident { manufacturer : String::from_utf8_lossy(& m ).into_owned() 
                  , board        : String::from_utf8_lossy(& b ).into_owned() 
                  , firmware     : f  
                  } )
    }

    pub fn get_id(&mut self) -> Result<Vec<u8>,SPIError> {
        self.spi_read_vec(GetStringCmd::GetId, 20)
    }   

    pub fn set_led(&mut self, value: u8) -> Result<(),SPIError> {
        self.spi_write_8(WriteU8Cmd::SetLed, value)
    }

    pub fn get_voltage(&mut self, volt_rail : GetVoltageCmd) -> Result<f32,SPIError>
    {
        let v = self.spi_read_16(volt_rail as u8) ?;
        Ok( f32::from(v) / 1000.0 )
    }
    
    pub fn set_sensor_type(&mut self, port : SensorPort , sensor_type : SensorType , flags : u16)
        -> Result<(),SPIError>
    {
        // remember the new sensor type
        self.sensor_type[port as usize] = sensor_type;

        let send_array =
            match sensor_type {
                SensorType::Custom => 
                    vec![port.as_bitfield(), sensor_type as u8, flags.shr(8) as u8 , flags as u8] ,
                SensorType::I2c => 
                    panic!("SensorType::I2c is not yet implemented."),
                _ => 
                    vec![port.as_bitfield(), sensor_type as u8, 0 , 0] 
            };
        
        self.spi_send_vec(SendArrayCmd::SetSensorType , send_array)
    }



    // pub fn transact_i2c // TODO

    
    pub fn read_sensor(&mut self, port: SensorPort) -> Result<SensorData,SensorError>
    {   
        let conf_sensor_type = self.sensor_type[port as usize];

        let transfer_length =
            match conf_sensor_type {
                SensorType::None => Err(SensorError::NotConfigured),
                SensorType::I2c => Err(SensorError::NotImplemented), 
                SensorType::Custom => Ok(10),
                SensorType::Touch | SensorType::TouchNxt | SensorType::TouchEv3 
                    => Ok(7),
                SensorType::NxtLightOn | SensorType::NxtLightOff 
                | SensorType::NxtColorRed | SensorType::NxtColorGreen 
                | SensorType::NxtColorBlue | SensorType::NxtColorFull 
                | SensorType::NxtColorOff 
                    => Ok(8),
                SensorType::NxtUltrasonic => Ok(7),
                SensorType::Ev3GyroAbs | SensorType::Ev3GyroDps => Ok(8),
                SensorType::Ev3GyroAbsDps => Ok(10),
                SensorType::Ev3ColorReflected | SensorType::Ev3ColorAmbient
                | SensorType::Ev3ColorColor 
                    => Ok(7),
                SensorType::Ev3ColorRawReflected => Ok(10),
                SensorType::Ev3ColorColorComponents => Ok(14),
                SensorType::Ev3UltrasonicCm | SensorType::Ev3UltrasonicInches => Ok(8),
                SensorType::Ev3UltrasonicListen => Ok(7),
                SensorType::Ev3InfraredProximity => Ok(7),
                SensorType::Ev3InfraredSeek => Ok(14),
                SensorType::Ev3InfraredRemote => Ok(10),
            } ? ;
        let send_buf = vec![0; transfer_length - 2 ]; // -2 is from send header
        let recv_buf = self.spi_send_read_vec(SendReadArrayCmd::GetSensor1 as u8 
                                                + port as u8 , send_buf) ?;
        // Now recv_buf is vec<u8> with (transfer_length-4) elements, so at least 3

        // construct some handy shorthands
        let recv_sensor_type = recv_buf[0];
        let raw_i8 = recv_buf[2] as i8;
        // Here we use closures, because recv_buf may be too short
        let raw_fst_i16 = || (recv_buf[2] as i16).shl(8) | (recv_buf[3] as i16);
        let raw_snd_i16 = || (recv_buf[4] as i16).shl(8) | (recv_buf[5] as i16);
        
        // check that the reported and expected sensor types match
        if recv_sensor_type != conf_sensor_type as u8 {
            if conf_sensor_type == SensorType::Touch
               && ( recv_sensor_type == SensorType::TouchEv3 as u8
                 || recv_sensor_type == SensorType::TouchNxt as u8) {
                ()  // this is allowed
              } else {
                println!("Expected {:?}, BrickPi3 reported {:?}", conf_sensor_type, recv_sensor_type);
                return Err(SensorError::TypeMismatch)
              }
        }

        // Check that the sensor indicated valid data
        match recv_buf[1] {
            0 => () , // valid data -> continue
            1 => return Err(SensorError::NotConfigured) ,
            2 => return Err(SensorError::Configuring) ,
            3 => return Err(SensorError::NoData) ,
            4 => return Err(SensorError::I2cError) ,
            e => return Err(SensorError::UnknownStatusReported(e)) ,
        }

        // Produce result SensorData
        match conf_sensor_type {
            SensorType::None => Err(SensorError::NotImplemented),
            SensorType::I2c => Err(SensorError::NotImplemented), 

            SensorType::Custom 
                => Ok(SensorData::Custom 
                        { adc1: ((recv_buf[4] & 0xF as u8) as u16).shl(8) | recv_buf[5] as u16
                        , adc6: (recv_buf[4].shr(4) as u16) | (recv_buf[3] as u16).shl(4)
                        , pin5: (recv_buf[2] & 1) != 0  // test bit 0
                        , pin6: (recv_buf[2] & 2) != 0  // test bit 1
                        }  ) ,

            SensorType::Touch | SensorType::TouchNxt | SensorType::TouchEv3 
                => Ok(SensorData::Touch{ pressed: raw_i8 != 0 }) ,

            SensorType::NxtLightOn 
                => Ok(SensorData::LightReflected{ brightness: raw_fst_i16() as u16 }) ,
            SensorType::NxtLightOff 
                => Ok(SensorData::LightAmbient{ brightness: raw_fst_i16() as u16 }) ,

            SensorType::NxtColorRed
                => Ok(SensorData::Color
                        { red: raw_fst_i16(), green: 0, blue: 0
                        , color: 0 , ambient: 0} ) ,
            SensorType::NxtColorGreen 
                => Ok(SensorData::Color
                        { red: 0, green: raw_fst_i16(), blue: 0
                        , color: 0 , ambient: 0} ) ,
            SensorType::NxtColorBlue 
                => Ok(SensorData::Color
                        { red: 0, green: 0, blue: raw_fst_i16()
                        , color: 0 , ambient: 0} ) ,
            SensorType::NxtColorFull 
                => Ok(SensorData::Color
                        { color:   recv_buf[2] as i8
                        , red:     (recv_buf[3] as i16).shl(2) | ((recv_buf[7] as i16).shr(6) & (0x03 as i16))
                        , green:   (recv_buf[4] as i16).shl(2) | ((recv_buf[7] as i16).shr(4) & (0x03 as i16))
                        , blue:    (recv_buf[5] as i16).shl(2) | ((recv_buf[7] as i16).shr(2) & (0x03 as i16))
                        , ambient: (recv_buf[6] as i16).shl(2) | ((recv_buf[7] as i16).shr(0) & (0x03 as i16))
                        } ) ,
            SensorType::NxtColorOff 
                => Ok(SensorData::Color
                        { red: 0, green: 0, blue: 0
                        , color: 0 , ambient: raw_fst_i16()} ) ,

            SensorType::NxtUltrasonic
                => Ok(SensorData::UltrasonicDistance{ meters: raw_i8 as f32 / 100.0 } ) ,

            SensorType::Ev3GyroAbs
                => Ok(SensorData::Gyro {abs: raw_fst_i16() , dps: 0             }) ,
            SensorType::Ev3GyroDps
                => Ok(SensorData::Gyro {abs: 0             , dps: raw_fst_i16() }) , 
            SensorType::Ev3GyroAbsDps 
                => Ok(SensorData::Gyro {abs: raw_fst_i16() , dps: raw_snd_i16() }) ,

            SensorType::Ev3ColorReflected
                => Ok(SensorData::Color
                        { red: raw_fst_i16(), green: 0, blue: 0
                        , color: 0 , ambient: 0} ) ,
            SensorType::Ev3ColorAmbient
                => Ok(SensorData::Color
                        { red: 0, green: 0, blue: 0
                        , color: 0 , ambient: raw_i8 as i16} ) ,
            SensorType::Ev3ColorColor 
                => Ok(SensorData::Color
                        { red: 0, green: 0, blue: 0
                        , color: raw_i8 , ambient: 0} ) ,
            SensorType::Ev3ColorRawReflected 
                => Ok(SensorData::Color
                        { red: raw_fst_i16(), green: 0, blue: 0
                        , color: 0 , ambient: 0} ) ,
            SensorType::Ev3ColorColorComponents 
                => Ok(SensorData::Color
                        { red:   (recv_buf[2] as i16).shl(8) | (recv_buf[3] as i16)
                        , green: (recv_buf[4] as i16).shl(8) | (recv_buf[5] as i16)
                        , blue:  (recv_buf[6] as i16).shl(8) | (recv_buf[7] as i16)
                        , color: 0 
                        , ambient: 0
                        } ) ,

            SensorType::Ev3UltrasonicCm 
                => Ok(SensorData::UltrasonicDistance{ meters: raw_fst_i16() as f32 / 1000.0 }) ,
            SensorType::Ev3UltrasonicInches 
                => Ok(SensorData::UltrasonicDistance{ meters: raw_fst_i16() as f32 * 0.00254 }) , // TODO
            SensorType::Ev3UltrasonicListen
                => Ok(SensorData::UltrasonicPresence{ presence: raw_i8 != 0 } ) ,

            SensorType::Ev3InfraredProximity  
                => Err(SensorError::NotImplemented) , // TODO
            SensorType::Ev3InfraredSeek 
                => Err(SensorError::NotImplemented) , // TODO
            SensorType::Ev3InfraredRemote
                =>  Ok( SensorData::InfraredRemote{ remote:
                            recv_buf[2..6]
                            .iter()
                            .map( |i| match *i {
                                        1  => RemoteButtons::RED_UP ,
                                        2  => RemoteButtons::RED_DOWN ,
                                        3  => RemoteButtons::BLUE_UP ,
                                        4  => RemoteButtons::BLUE_DOWN ,
                                        5  => RemoteButtons::RED_UP | RemoteButtons::BLUE_UP ,
                                        6  => RemoteButtons::RED_UP | RemoteButtons::BLUE_DOWN ,
                                        7  => RemoteButtons::RED_DOWN | RemoteButtons::BLUE_UP ,
                                        8  => RemoteButtons::RED_DOWN | RemoteButtons::BLUE_DOWN ,
                                        9  => RemoteButtons::BROADCAST,
                                        10 => RemoteButtons::RED_UP | RemoteButtons::RED_DOWN ,
                                        11 => RemoteButtons::BLUE_UP | RemoteButtons::BLUE_DOWN ,
                                        _  => RemoteButtons::empty(),
                                    }
                                ).collect() } 
                    )
        }
    }


    pub fn set_motor_power(&mut self, port : MotorPort, power: i8) -> Result<(),SPIError>
    {
        self.spi_send_vec(SendArrayCmd::SetMotorPower, vec![port.as_bitfield(), power as u8])
    }
    
    pub fn set_motor_position(&mut self, port : MotorPort, pos: i32) -> Result<(),SPIError>
    {
        self.spi_send_vec( SendArrayCmd::SetMotorPosition
            , vec![ port.as_bitfield()
                  , pos.shr(24) as u8 , pos.shr(16) as u8, pos.shr(8) as u8 , pos as u8])   
    }
    
    // This is different from C++ version. Only sets one motor per call.
    pub fn set_motor_position_relative(&mut self, port : MotorPort, position: i32) -> Result<(),SPIError>
    {
        let enc = self.read_motor_encoder(port) ?;
        self.set_motor_position(port, enc+position)
    }
    
    pub fn set_motor_dps(&mut self, port : MotorPort, dps: i16) -> Result<(),SPIError>
    {
        self.spi_send_vec( SendArrayCmd::SetMotorDps
            , vec![ port.as_bitfield(), dps.shr(8) as u8 , dps as u8])
    }

    pub fn set_motor_limits(&mut self, port : MotorPort, power : u8, dps : u16) -> Result<(),SPIError>
    {
        self.spi_send_vec( SendArrayCmd::SetMotorLimits
            , vec![ port.as_bitfield() , power, dps.shr(8) as u8 , dps as u8] )
    }
    
    pub fn read_motor_status(&mut self, port: MotorPort ) -> Result<MotorStatus,SPIError>
    {

        let cmd = SendReadArrayCmd::GetMotorAStatus as u8 + port as u8;
        let cmd_buf : Vec<u8> = vec![0; 10]; // payload 10 bytes + header 2 bytes
        let resp = self.spi_send_read_vec( cmd , cmd_buf ) ?;
        Ok(MotorStatus  { state: resp[0] 
                        , power: resp[1] as i8
                        , position: (resp[2] as i32).shl(24) | (resp[3] as i32).shl(16) 
                                    | (resp[4] as i32).shl(8) | (resp[5] as i32)
                        , dps: (resp[6] as i16).shl(8) | resp[7] as i16 } )
    }
    
    
    pub fn offset_motor_encoder(&mut self, port:MotorPort, position: i32) -> Result<(),SPIError>
    {
        let outvec = vec![ port.as_bitfield() 
                         , position.shr(24) as u8 , position.shr(16) as u8
                         , position.shr(8) as u8 , position as u8
                         ];
        self.spi_send_vec( SendArrayCmd::OffsetMotorEncoder , outvec )
    }

    // returns the value of the encoder before reset to zero
    pub fn reset_motor_encoder(&mut self, port: MotorPort) -> Result<i32,SPIError>
    {
        let v = self.read_motor_encoder(port) ?;
        self.offset_motor_encoder(port, v) ?;
        Ok(v)
    }
    
    pub fn read_motor_encoder(&mut self, port: MotorPort ) -> Result<i32,SPIError>
    {
        let cmd = match port {
            MotorPort::PortA => ReadU32Cmd::GetMotorAEncoder ,
            MotorPort::PortB => ReadU32Cmd::GetMotorBEncoder ,
            MotorPort::PortC => ReadU32Cmd::GetMotorCEncoder ,
            MotorPort::PortD => ReadU32Cmd::GetMotorDEncoder ,
        };
        let v = self.spi_read_32(cmd) ?;
        Ok( v as i32 )
    }
    
    pub fn reset_all(&mut self) -> Result<(),SPIError>
    {
        // The control flow here tries to execute all of the messages regardless of the
        // returned error codes, and only afterwards combines the error codes.
        let sensor_result =  
        SensorPort::iter()
            .map( |s| self.set_sensor_type( s , SensorType::None , 0))
            .fold( Ok(()) , |r1,r2| r1.and(r2) );

        let motor_result = 
        MotorPort::iter()
            .map( |m| { let p = self.set_motor_power( m , MOTOR_FLOAT );
                        let l = self.set_motor_limits( m , 0 , 0);
                        let sl = self.set_led(LED_TO_FIRMWARE_CONTROL);
                        p.and(l).and(sl)
                      }
                )
            .fold( Ok(()) , |r1,r2| r1.and(r2) );

        sensor_result.and(motor_result)
    }


    // Internal functions
    // --------------------------------------------


    fn spi_read_vec(&mut self, msg_type: GetStringCmd , str_len: usize) 
                    -> Result<Vec<u8>,SPIError> 
    {
        if str_len + 4 > LONGEST_SPI_TRANSFER {
            Err(SPIError::TooLongSPITransfer)
        } else {
            let xfer = 4 + str_len;
            self.txbuf[0] = self.address;
            self.txbuf[1] = msg_type as u8;
            {
                let mut transfer = SpidevTransfer
                        ::read_write(&self.txbuf[0..xfer], &mut self.rxbuf[0..xfer]);
                try!(self.spidev.transfer(&mut transfer));
            }
            if self.rxbuf[3] != 0xA5 {
                Err(SPIError::BadResponse)
            } else {
                Ok( self.rxbuf[4..4+str_len].to_vec() )
            }
        }
    }

    fn spi_send_vec(&mut self, msg_type: SendArrayCmd, data: Vec<u8>) -> Result<(),SPIError>
    {
        let xfer = 2 + data.len();
        if xfer > LONGEST_SPI_TRANSFER {
            Err(SPIError::TooLongSPITransfer)
        } else {

            self.txbuf[0] = self.address;
            self.txbuf[1] = msg_type as u8;
            (&mut self.txbuf[2..xfer]).copy_from_slice(&data);
            let mut transfer = SpidevTransfer
                        ::read_write(&self.txbuf[0..xfer], &mut self.rxbuf[0..xfer]);
            try!(self.spidev.transfer(&mut transfer ));
            Ok(())
        }
    }
    
    // Note: This expects N bytes to send and returns N-2 bytes
    fn spi_send_read_vec(&mut self, msg_type: u8, data_out: Vec<u8>) -> Result<Vec<u8>,SPIError> 
    {
        let xfer = 2 + data_out.len();
        if xfer > LONGEST_SPI_TRANSFER {
            Err(SPIError::TooLongSPITransfer)
        } else {
            self.txbuf[0] = self.address;
            self.txbuf[1] = msg_type as u8;
            (&mut self.txbuf[2..xfer]).copy_from_slice(&data_out);
            {
                let mut transfer = SpidevTransfer
                            ::read_write(&self.txbuf[0..xfer], &mut self.rxbuf[0..xfer]);
                try!(self.spidev.transfer(&mut transfer ));
            }
            if self.rxbuf[3] != 0xA5 {
                Err(SPIError::BadResponse)
            } else {
                Ok( self.rxbuf[4..xfer].to_vec() )
            }
        }

    }
    
    fn spi_read_32(&mut self, msg_type: ReadU32Cmd) -> Result<u32,SPIError>
    {
        self.txbuf[0] = self.address;
        self.txbuf[1] = msg_type as u8;
        {
            let mut transfer = SpidevTransfer
                    ::read_write(&self.txbuf[0..8], &mut self.rxbuf[0..8]);
            try!(self.spidev.transfer(&mut transfer));
        }
        if self.rxbuf[3] != 0xA5 {
            Err(SPIError::BadResponse)
        } else {
            Ok( u32::from(self.rxbuf[4]).shl(24) |
                u32::from(self.rxbuf[5]).shl(16) |
                u32::from(self.rxbuf[6]).shl(8) |
                u32::from(self.rxbuf[7]) )      
        }
    }

    fn spi_read_16(&mut self, msg_type: u8) -> Result<u16,SPIError>
    {
        self.txbuf[0] = self.address;
        self.txbuf[1] = msg_type as u8;
        {
            let mut transfer = SpidevTransfer
                    ::read_write(&self.txbuf[0..6], &mut self.rxbuf[0..6]);
            try!(self.spidev.transfer(&mut transfer));
        }
        if self.rxbuf[3] != 0xA5 {
            Err(SPIError::BadResponse)
        } else {
            Ok( u16::from(self.rxbuf[4]).shl(8) +
                u16::from(self.rxbuf[5]) )      
        }
    }

    fn spi_write_8(&mut self, msg_type: WriteU8Cmd, value: u8) -> Result<(),SPIError>
    {
        self.txbuf[0] = self.address;
        self.txbuf[1] = msg_type as u8;
        self.txbuf[2] = value;
        {
            let mut transfer = SpidevTransfer
                    ::read_write(&self.txbuf[0..3], &mut self.rxbuf[0..3]);
            try!(self.spidev.transfer(&mut transfer));
        }
        Ok(())
    }


}

