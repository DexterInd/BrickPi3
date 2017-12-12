//
// This code is an example for detecting BrickPi3 and reading information from it.
//
// Copyright (C) 2017 Juhana Helovuo <juhe@iki.fi>
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
//
//
// Results: Print information about the attached BrickPi3.
//
// Compilation command, in the crate top directory (brickpi3)
//   cargo build --example info
 
extern crate brickpi3;

fn main() {
    match brickpi3::BrickPi3::open("/dev/spidev0.1") {
        Err(why) =>  println!("Opening BrickPi3 SPI device failed: {:?}", why) ,
        Ok(mut bp) => {
            println!("SPI device opened.");
            match bp.detect() {
                Err(why) => println!("BrickPi3 detection failed: {:?}", why) ,
                Ok(ident) => {
                    println!("Detected BrickPi3.");
                    println!("Manufacturer    :{}", ident.manufacturer);
                    println!("Board           :{}", ident.board);
                    println!("Firmware        :{} ({})"
                                , brickpi3::version_as_String(ident.firmware)
                                , ident.firmware );
                    println!("Battery voltage : {:.3}"
                            , bp.get_voltage(brickpi3::GetVoltageCmd::VoltBattery).unwrap() );
                    println!("9V voltage      : {:.3}"
                            , bp.get_voltage(brickpi3::GetVoltageCmd::Volt9v).unwrap() );
                    println!("5V voltage      : {:.3}"
                            , bp.get_voltage(brickpi3::GetVoltageCmd::Volt5v).unwrap() );
                    println!("3.3V voltage    : {:.3}"
                            , bp.get_voltage(brickpi3::GetVoltageCmd::Volt3v3).unwrap() );
                }   
            }
        }
    }
}

