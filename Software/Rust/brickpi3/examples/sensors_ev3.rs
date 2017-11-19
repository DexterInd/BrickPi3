//
// This code is an example for reading the encoders of motors connected to the BrickPi3.
//
// Copyright (C) 2017 Juhana Helovuo <juhe@iki.fi>
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
//
// Hardware: Connect EV3 sensors to the sensor ports. Color sensor to PORT_1. 
// Ultrasonic sensor to PORT_2. Gyro sensor to PORT_3. Infrared sensor to PORT_4.
//
//  Results:  When you run this program, once the sensors have a few seconds to get configured, 
// you should see the values for each sensor.
//
// Compilation command, in the crate top directory (brickpi3)
//   cargo build --example sensors_ev3

extern crate brickpi3;
extern crate ctrlc;
extern crate strum; // strum is for iterating over enums
// #[macro_use] extern crate strum_macros;

use std::{thread, time};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
//use strum::IntoEnumIterator;
use brickpi3::*;

fn main() {
	match brickpi3::BrickPi3::open("/dev/spidev0.1") {
		Err(why) =>  println!("Opening BrickPi3 SPI device failed: {:?}", why) ,
		Ok(mut bp) => {
			match bp.detect() {
				Err(why) => println!("BrickPi3 detection failed: {:?}", why) ,
				Ok(_ident) => {
					match do_sensors(&mut bp) {
						Err(why) => { println!("BrickPi error: {:?}", why);
									  bp.reset_all()
									  	.unwrap_or_else(|e| println!("{:?}",e))	
									},
						Ok(()) => ()
					}
				}
			}
		}
	}
}

fn do_sensors(bp: &mut BrickPi3) -> Result<(),SPIError> {
	// Set signal handler for Ctrl-C
	let running = Arc::new(AtomicBool::new(true));
    let r = running.clone();
    ctrlc::set_handler(move || {
        r.store(false, Ordering::SeqCst);
    }).expect("Error setting Ctrl-C handler");

    bp.set_sensor_type(SensorPort::Port1, SensorType::Ev3ColorColorComponents, 0) ? ;
    bp.set_sensor_type(SensorPort::Port2, SensorType::Ev3UltrasonicCm, 0) ? ;
    bp.set_sensor_type(SensorPort::Port3, SensorType::Ev3GyroAbsDps, 0) ? ;
    bp.set_sensor_type(SensorPort::Port4, SensorType::Ev3InfraredRemote, 0) ? ;
    


    // loop until interrupted
    while running.load(Ordering::SeqCst) {
        match bp.read_sensor(SensorPort::Port1) {
            Ok(SensorData::Color{red,green,blue, ..}) =>
                print!("S1: r={:} g={:} b={:} ", red,green,blue),
            what => print!("S1: unexpected {:?}", what),
        }

        match bp.read_sensor(SensorPort::Port2) {
            Ok(SensorData::UltrasonicDistance{ meters }) =>
                print!("S2: ultrasonic {:.2} meters ", meters),
            what => print!("S2: unexpected {:?}", what),
        }

        match bp.read_sensor(SensorPort::Port3) {
            Ok(SensorData::Gyro{ abs, dps }) =>
                print!("S3: gyro {:.2} deg/s  {:.2} deg ", dps, abs),
            what => print!("S3: unexpected {:?}", what),
        } 

        match bp.read_sensor(SensorPort::Port4) {
            Ok(SensorData::InfraredRemote{ remote }) =>
                print!("S4: remote {:2x} {:2x} {:2x} {:2x} "
                        , remote[0], remote[1], remote[2], remote[3]),
            what => print!("S4: unexpected {:?}", what),
        } 

        println!("");
    	// wait 50ms before next iteration
    	thread::sleep(time::Duration::from_millis(50));

    }
    // ensure no motors are left running
    bp.reset_all()
}

	
    
    