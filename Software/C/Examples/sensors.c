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
 *    g++ -o program "sensors.c"
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
  
  int error;
  
/*  BP.set_sensor_type(PORT_1, SENSOR_TYPE_CUSTOM, SENSOR_CONFIG_REPORT_1_ADC | SENSOR_CONFIG_REPORT_6_ADC);
  BP.set_sensor_type(PORT_2, SENSOR_TYPE_TOUCH);
  BP.set_sensor_type(PORT_3, SENSOR_TYPE_NXT_ULTRASONIC);
  BP.set_sensor_type(PORT_4, SENSOR_TYPE_NXT_COLOR_FULL);
  
  int32_t Sensor1[4];
  int32_t Sensor2[1];
  int32_t Sensor3[1];
  int32_t Sensor4[5];
  
  while(true){
    error = BP.get_sensor(PORT_1, Sensor1);
    printf("get_sensor 1: %d", error);
    BP.get_sensor(PORT_2, Sensor2);
    printf("  2: %d", error);
    BP.get_sensor(PORT_3, Sensor3);
    printf("  3: %d", error);
    BP.get_sensor(PORT_4, Sensor4);
    printf("  4: %d", error);
    printf("  Values 1: %4d %4d %d %d  2: %d  3: %3d  4: %d %4d %4d %4d %4d\n", Sensor1[0], Sensor1[1], Sensor1[2], Sensor1[3], Sensor2[0], Sensor3[0], Sensor4[0], Sensor4[1], Sensor4[2], Sensor4[3], Sensor4[4]);
    */
  BP.set_sensor_type(PORT_1, SENSOR_TYPE_EV3_COLOR_COLOR_COMPONENTS);
  BP.set_sensor_type(PORT_2, SENSOR_TYPE_EV3_ULTRASONIC_CM);
  BP.set_sensor_type(PORT_3, SENSOR_TYPE_EV3_INFRARED_SEEK);
  BP.set_sensor_type(PORT_4, SENSOR_TYPE_EV3_INFRARED_REMOTE);
  
  int32_t Sensor1[4];
  int32_t Sensor2[1];
  int32_t Sensor3[8];
  int32_t Sensor4[4];
  
  while(true){
    error = BP.get_sensor(PORT_1, Sensor1);
    printf("get_sensor 1: %d", error);
    BP.get_sensor(PORT_2, Sensor2);
    printf("  2: %d", error);
    BP.get_sensor(PORT_3, Sensor3);
    printf("  3: %d", error);
    BP.get_sensor(PORT_4, Sensor4);
    printf("  4: %d", error);
    printf("  Values 1: %4d %4d %d %d  2: %d  3: %3d  4: %d %4d %4d %4d %4d\n", Sensor1[0], Sensor1[1], Sensor1[2], Sensor1[3], Sensor2[0], Sensor3[0], Sensor4[0], Sensor4[1], Sensor4[2], Sensor4[3], Sensor4[4]);
    
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
