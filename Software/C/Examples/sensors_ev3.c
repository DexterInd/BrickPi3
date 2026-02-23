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
 *  Hardware: Connect EV3 sensors to the sensor ports. Color sensor to PORT_1. Ultrasonic sensor to PORT_2. Gyro sensor to PORT_3. Infrared sensor to PORT_4.
 *
 *  Results:  When you run this program, once the sensors have a few seconds to get configured, you should see the values for each sensor.
 *
 *  Example compile command:
 *    g++ -o program "sensors_ev3.c"
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

  int error;

  BP.set_sensor_type(PORT_1, SENSOR_TYPE_EV3_COLOR_COLOR_COMPONENTS);
  BP.set_sensor_type(PORT_2, SENSOR_TYPE_EV3_ULTRASONIC_CM);
  BP.set_sensor_type(PORT_3, SENSOR_TYPE_EV3_GYRO_ABS_DPS);
  BP.set_sensor_type(PORT_4, SENSOR_TYPE_EV3_INFRARED_REMOTE);

  sensor_color_t      Color1;
  sensor_ultrasonic_t Ultrasonic2;
  sensor_gyro_t       Gyro3;
  sensor_infrared_t   Infrared4;

  while(true){
    error = 0;

    if(BP.get_sensor(PORT_1, &Color1)){
      error++;
    }else{
      printf("Color sensor (S1): red %4d green %4d blue %4d   ", Color1.reflected_red, Color1.reflected_green, Color1.reflected_blue);
    }

    if(BP.get_sensor(PORT_2, &Ultrasonic2)){
      error++;
    }else{
      printf("Ultrasonic sensor (S2): CM %5.1f Inches %5.1f   ", Ultrasonic2.cm, Ultrasonic2.inch);
    }

    if(BP.get_sensor(PORT_3, &Gyro3)){
      error++;
    }else{
      printf("Gyro sensor (S3): absolute %5d degrees per second %4d   ", Gyro3.abs, Gyro3.dps);
    }

    if(BP.get_sensor(PORT_4, &Infrared4)){
      error++;
    }else{
      printf("Infrared sensor (S4): channel 1 %02X channel 2 %02X channel 3 %02X channel 4 %02X   ", Infrared4.remote[0], Infrared4.remote[1], Infrared4.remote[2], Infrared4.remote[3]);
    }

    if(error == 4){
      printf("Waiting for sensors to be configured");
    }

    printf("\n");

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
