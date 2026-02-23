/*
 *  https://www.dexterindustries.com/BrickPi/
 *  https://github.com/DexterInd/BrickPi3
 *
 *  Copyright (c) 2026 Modular Robotics Inc
 *  Released under the MIT license (http://choosealicense.com/licenses/mit/).
 *  For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
 *
 *  This code is an example for reading the encoders of motors connected to the BrickPi3.
 *
 *  Hardware: Connect EV3 or NXT motor(s) to any of the BrickPi3 motor ports.
 *
 *  Results:  When you run this program, you should see the encoder value for each motor.
 * By manually rotating motor A, the other motor(s) will be controlled.
 * Motor B power will be controlled, Motor C speed will be controlled,
 * and motor D position will be controlled.
 *
 *  Example compile command:
 *    g++ -o program "motors.c"
 *  Example run command:
 *    sudo ./program
 *
 */

#include "../BrickPi3.cpp" // for BrickPi3
#include <stdio.h>      // for printf
#include <unistd.h>     // for usleep
#include <signal.h>     // for catching exit signals

BrickPi3 BP;

void exit_signal_handler(int signo);

int main(){
  signal(SIGINT, exit_signal_handler); // register the exit function for Ctrl+C

  BP.detect(); // Make sure that the BrickPi3 is communicating and that the firmware is compatible with the drivers.

  // Reset the encoders
  BP.reset_motor_encoder(PORT_A + PORT_B + PORT_C + PORT_D);

  // Veriables for reading motor state bits
  uint8_t StateA, StateB, StateC, StateD;

  // Variables for reading motor powers
  int8_t PowerA, PowerB, PowerC, PowerD;

  // Variables for reading motor encoder positions
  int32_t PositionA, PositionB, PositionC, PositionD;

  // Variables for reading motor speeds (Degrees Per Second)
  int16_t DPSA, DPSB, DPSC, DPSD;

  while(true){
    // Read the motor status values
    BP.get_motor_status(PORT_A, StateA, PowerA, PositionA, DPSA);
    BP.get_motor_status(PORT_B, StateB, PowerB, PositionB, DPSB);
    BP.get_motor_status(PORT_C, StateC, PowerC, PositionC, DPSC);
    BP.get_motor_status(PORT_D, StateD, PowerD, PositionD, DPSD);

    // Use the encoder value from motor A to control motors B, C, and D
    BP.set_motor_power(PORT_B, PositionA < 100 ? PositionA > -100 ? PositionA : -100 : 100);
    BP.set_motor_dps(PORT_C, PositionA);
    BP.set_motor_position(PORT_D, PositionA);

    // Display the encoder values
    printf("State A: %d  B: %d  C: %d  D: %d  Power A: %4d  B: %4d  C: %4d  D: %4d  Encoder A: %6d  B: %6d  C: %6d  D: %6d  DPS A: %6d  B: %6d  C: %6d  D: %6d\n", StateA, StateB, StateC, StateD, PowerA, PowerB, PowerC, PowerD, PositionA, PositionB, PositionC, PositionD, DPSA, DPSB, DPSC, DPSD);

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
