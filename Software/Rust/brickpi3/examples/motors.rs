//
// This code is an example for reading the encoders of motors connected to the BrickPi3.
//
// Copyright (C) 2017 Juhana Helovuo <juhe@iki.fi>
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
//
// Hardware: Connect EV3 or NXT motor(s) to any of the of the BrickPi3 motor ports.
//
// Results:  When you run this program, you should see the encoder value for
// each motor. By manually rotating motor A, the other motor(s) will be
// controlled. Motor B power will be controlled, Motor C speed will be
// controlled, and motor D position will be controlled.
//
// Compilation command, in the crate top directory (brickpi3)
//   cargo build --example motors

extern crate brickpi3;
extern crate ctrlc;
extern crate strum; // strum is for iterating over enums
// #[macro_use] extern crate strum_macros;

use std::{thread, time};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use strum::IntoEnumIterator;
use brickpi3::*;

fn main() {
	match brickpi3::BrickPi3::open("/dev/spidev0.1") {
		Err(why) =>  println!("Opening BrickPi3 SPI device failed: {:?}", why) ,
		Ok(mut bp) => {
			match bp.detect() {
				Err(why) => println!("BrickPi3 detection failed: {:?}", why) ,
				Ok(_ident) => {
					match run_motors(&mut bp) {
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

fn run_motors(bp: &mut BrickPi3) -> Result<(),SPIError> {
	// Set signal handler for Ctrl-C
	let running = Arc::new(AtomicBool::new(true));
    let r = running.clone();
    ctrlc::set_handler(move || {
        r.store(false, Ordering::SeqCst);
    }).expect("Error setting Ctrl-C handler");

    // reset all motor encoders
    for mp in MotorPort::iter() {
    	bp.reset_motor_encoder(mp)
    		.unwrap_or_else(|e| {println!("{:?}",e); 0} );
    }

    // loop until interrupted
    while running.load(Ordering::SeqCst) {
    	let enc_a = bp.read_motor_encoder(MotorPort::PortA) ?;
    	let enc_b = bp.read_motor_encoder(MotorPort::PortB) ?;
    	let enc_c = bp.read_motor_encoder(MotorPort::PortC) ?;
    	let enc_d = bp.read_motor_encoder(MotorPort::PortD) ?;

    	bp.set_motor_power(	MotorPort::PortB
    						, if enc_a < 100 
    							{if enc_a > -100 {enc_a as i8} else {-100}} 
    						  else {100} 
    						) ?;
    	bp.set_motor_dps( MotorPort::PortC, enc_a as i16) ? ;
    	bp.set_motor_position(MotorPort::PortD , enc_a) ? ;

    	println!("Encoders A: {:.2 } B: {:.2 } C: {:.2 } D: {:.2 }", enc_a, enc_b, enc_c, enc_d);

    	// wait 200ms before next iteration
    	thread::sleep(time::Duration::from_millis(200));

    }
    // ensure no motors are left running
    bp.reset_all()
}

	
    
    