/*
 *  https://www.dexterindustries.com/BrickPi/
 *  https://github.com/DexterInd/BrickPi3
 *
 *  Copyright (c) 2017 Dexter Industries
 *  Released under the MIT license (http://choosealicense.com/licenses/mit/).
 *  For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
 *
 *  This code is an example for reading the encoders of motors connected to the BrickPi3.
 *
 *  Hardware: Connect EV3 or NXT motor(s) to any of the BrickPi3 motor ports.
 *
 *  Results:  When you run this program, you should see the encoder value for each motor. By manually rotating motor A, the other motor(s) will be controlled. Motor B power will be controlled, Motor C speed will be controlled, and motor D position will be controlled.
 *
 *  Example compile command:
 *    g++ -o program "motors.c"
 *  Example run command:
 *    sudo ./program
 *
 */

#include "BrickPi3.cpp" // for BrickPi3
#include <stdio.h>      // for printf
#include <unistd.h>     // for usleep
#include <signal.h>     // for catching exit signals

BrickPi3 BP;

void exit_signal_handler(int signo);

int main(){
  signal(SIGINT, exit_signal_handler); // register the exit function for Ctrl+C
  
  BP.detect(); // Make sure that the BrickPi3 is communicating and that the firmware is compatible with the drivers.
  
  // Reset the encoders
  BP.offset_motor_encoder(PORT_A, BP.get_motor_encoder(PORT_A));
  BP.offset_motor_encoder(PORT_B, BP.get_motor_encoder(PORT_B));
  BP.offset_motor_encoder(PORT_C, BP.get_motor_encoder(PORT_C));
  BP.offset_motor_encoder(PORT_D, BP.get_motor_encoder(PORT_D));
  
  while(true){
    // Read the encoders
    int32_t EncoderA = BP.get_motor_encoder(PORT_A);
    int32_t EncoderB = BP.get_motor_encoder(PORT_B);
    int32_t EncoderC = BP.get_motor_encoder(PORT_C);
    int32_t EncoderD = BP.get_motor_encoder(PORT_D);
    
    // Use the encoder value from motor A to control motors B, C, and D
    BP.set_motor_power(PORT_B, EncoderA < 100 ? EncoderA > -100 ? EncoderA : -100 : 100);
    BP.set_motor_dps(PORT_C, EncoderA);
    BP.set_motor_position(PORT_D, EncoderA);
    
    // Display the encoder values
    printf("Encoder A: %6d  B: %6d  C: %6d  D: %6d\n", EncoderA, EncoderB, EncoderC, EncoderD);
    
    // Delay for 20ms
    usleep(20000);
  }
}

// Signal handler that will be called when Ctrl+C is pressed to stop the program
void exit_signal_handler(int signo){
  if(signo == SIGINT){
    BP.reset_all();    // Reset everything so there are no run-away motors
    exit(-2);
  }
}
