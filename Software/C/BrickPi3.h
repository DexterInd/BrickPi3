/*
 *  https://www.dexterindustries.com/BrickPi/
 *  https://github.com/DexterInd/BrickPi3
 *
 *  Copyright (c) 2026 Modular Robotics Inc
 *  Released under the MIT license (http://choosealicense.com/licenses/mit/).
 *  For more information see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
 *
 *  C++ drivers for the BrickPi3
 */

#ifndef BrickPi3_h_
#define BrickPi3_h_

#define FIRMWARE_VERSION_REQUIRED "1.4." // Firmware version needs to start with this

#define LONGEST_SPI_TRANSFER 29 // longest possible message for configuring for an I2C sensor
#define LONGEST_I2C_TRANSFER 16 // longest possible I2C read/write

#define SPI_TARGET_SPEED 500000 // SPI target speed of 500kbps

#define SPIDEV_FILE_NAME "/dev/spidev0.1" // File name of SPI

#include <stdint.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>
#include <stdio.h>            // for printf
#include <string.h>           // for strstr

//#include <linux/types.h>
//#include <getopt.h>
//#include <unistd.h>

// Error values
#define ERROR_NONE                  0
#define ERROR_SPI_FILE             -1
#define ERROR_SPI_RESPONSE         -2
#define ERROR_WRONG_MANUFACTURER   -3
#define ERROR_WRONG_DEVICE         -4
#define ERROR_FIRMWARE_MISMATCH    -5
#define ERROR_SENSOR_TYPE_MISMATCH -6


// SPI message type
enum BPSPI_MESSAGE_TYPE{
  BPSPI_MESSAGE_NONE,

  BPSPI_MESSAGE_GET_MANUFACTURER,      // 1
  BPSPI_MESSAGE_GET_NAME,
  BPSPI_MESSAGE_GET_HARDWARE_VERSION,
  BPSPI_MESSAGE_GET_FIRMWARE_VERSION,
  BPSPI_MESSAGE_GET_ID,
  BPSPI_MESSAGE_SET_LED,
  BPSPI_MESSAGE_GET_VOLTAGE_3V3,
  BPSPI_MESSAGE_GET_VOLTAGE_5V,
  BPSPI_MESSAGE_GET_VOLTAGE_9V,
  BPSPI_MESSAGE_GET_VOLTAGE_VCC,
  BPSPI_MESSAGE_SET_ADDRESS,           // 11

  BPSPI_MESSAGE_SET_SENSOR_TYPE,       // 12

  BPSPI_MESSAGE_GET_SENSOR_1,          // 13
  BPSPI_MESSAGE_GET_SENSOR_2,
  BPSPI_MESSAGE_GET_SENSOR_3,
  BPSPI_MESSAGE_GET_SENSOR_4,

  BPSPI_MESSAGE_I2C_TRANSACT_1,        // 17
  BPSPI_MESSAGE_I2C_TRANSACT_2,
  BPSPI_MESSAGE_I2C_TRANSACT_3,
  BPSPI_MESSAGE_I2C_TRANSACT_4,

  BPSPI_MESSAGE_SET_MOTOR_POWER,

  BPSPI_MESSAGE_SET_MOTOR_POSITION,

  BPSPI_MESSAGE_SET_MOTOR_POSITION_KP,

  BPSPI_MESSAGE_SET_MOTOR_POSITION_KD, // 24

  BPSPI_MESSAGE_SET_MOTOR_DPS,         // 25

  BPSPI_MESSAGE_SET_MOTOR_DPS_KP,

  BPSPI_MESSAGE_SET_MOTOR_DPS_KD,

  BPSPI_MESSAGE_SET_MOTOR_LIMITS,

  BPSPI_MESSAGE_OFFSET_MOTOR_ENCODER,  // 29

  BPSPI_MESSAGE_GET_MOTOR_A_ENCODER,   // 30
  BPSPI_MESSAGE_GET_MOTOR_B_ENCODER,
  BPSPI_MESSAGE_GET_MOTOR_C_ENCODER,
  BPSPI_MESSAGE_GET_MOTOR_D_ENCODER,

  BPSPI_MESSAGE_GET_MOTOR_A_STATUS,    // 34
  BPSPI_MESSAGE_GET_MOTOR_B_STATUS,
  BPSPI_MESSAGE_GET_MOTOR_C_STATUS,
  BPSPI_MESSAGE_GET_MOTOR_D_STATUS
};

// Sensor type
enum SENSOR_TYPE{
  SENSOR_TYPE_NONE = 1, // Not configured for any sensor type
  SENSOR_TYPE_I2C,
  SENSOR_TYPE_CUSTOM,   // Choose 9v pullup, pin 5 and 6 configuration, and what to read back (ADC 1 and/or ADC 6 (always reports digital 5 and 6)).

  SENSOR_TYPE_TOUCH,    // Touch sensor. When this mode is selected, automatically configure for NXT/EV3 as necessary.
  SENSOR_TYPE_TOUCH_NXT,
  SENSOR_TYPE_TOUCH_EV3,

  SENSOR_TYPE_NXT_LIGHT_ON,
  SENSOR_TYPE_NXT_LIGHT_OFF,

  SENSOR_TYPE_NXT_COLOR_RED,
  SENSOR_TYPE_NXT_COLOR_GREEN,
  SENSOR_TYPE_NXT_COLOR_BLUE,
  SENSOR_TYPE_NXT_COLOR_FULL,
  SENSOR_TYPE_NXT_COLOR_OFF,

  SENSOR_TYPE_NXT_ULTRASONIC,

  SENSOR_TYPE_EV3_GYRO_ABS,
  SENSOR_TYPE_EV3_GYRO_DPS,
  SENSOR_TYPE_EV3_GYRO_ABS_DPS,

  SENSOR_TYPE_EV3_COLOR_REFLECTED,
  SENSOR_TYPE_EV3_COLOR_AMBIENT,
  SENSOR_TYPE_EV3_COLOR_COLOR,
  SENSOR_TYPE_EV3_COLOR_RAW_REFLECTED,
  SENSOR_TYPE_EV3_COLOR_COLOR_COMPONENTS,

  SENSOR_TYPE_EV3_ULTRASONIC_CM,
  SENSOR_TYPE_EV3_ULTRASONIC_INCHES,
  SENSOR_TYPE_EV3_ULTRASONIC_LISTEN,

  SENSOR_TYPE_EV3_INFRARED_PROXIMITY,
  SENSOR_TYPE_EV3_INFRARED_SEEK,
  SENSOR_TYPE_EV3_INFRARED_REMOTE
};

// Sensor states/error values
enum SENSOR_STATE{
  SENSOR_STATE_VALID_DATA,
  SENSOR_STATE_NOT_CONFIGURED,
  SENSOR_STATE_CONFIGURING,
  SENSOR_STATE_NO_DATA,
  SENSOR_STATE_I2C_ERROR        // Such as no ACK, SCL stretched too long, etc.
};

// Flags for configuring custom and I2C sensors
enum SENSOR_CONFIG_FLAGS{
  SENSOR_CONFIG_I2C_MID_CLOCK = 0x0001, // I2C. Send a clock pulse between reading and writing. Required by the NXT US sensor.
  SENSOR_CONFIG_PIN_1_PULL    = 0x0002, // I2C or custom. Enable 9v pullup on pin 1
  SENSOR_CONFIG_I2C_REPEAT    = 0x0004, // I2C. Keep performing the same transaction e.g. keep polling a sensor
  SENSOR_CONFIG_PIN_5_DIR     = 0x0010, // Custom. Set pin 5 output
  SENSOR_CONFIG_PIN_5_STATE   = 0x0020, // Custom. Set pin 5 high
  SENSOR_CONFIG_PIN_6_DIR     = 0x0100, // Custom. Set pin 6 output
  SENSOR_CONFIG_PIN_6_STATE   = 0x0200, // Custom. Set pin 6 high
  SENSOR_CONFIG_REPORT_1_ADC  = 0x1000, // Custom. Read pin 1 ADC
  SENSOR_CONFIG_REPORT_6_ADC  = 0x4000  // Custom. Read pin 6 ADC
};

// Sensor ports
#define PORT_1 0x01
#define PORT_2 0x02
#define PORT_3 0x04
#define PORT_4 0x08

// Motor ports
#define PORT_A 0x01
#define PORT_B 0x02
#define PORT_C 0x04
#define PORT_D 0x08

// Motor Float. Value to pass to set_motor_power to make a motor float.
#define MOTOR_FLOAT -128

// EV3 infrared remote button bit masks
#define REMOTE_BIT_RED_UP    0x01
#define REMOTE_BIT_RED_DOWN  0x02
#define REMOTE_BIT_BLUE_UP   0x04
#define REMOTE_BIT_BLUE_DOWN 0x08
#define REMOTE_BIT_BROADCAST 0x10

// structure for I2C
struct i2c_struct_t{
  uint8_t speed;
  uint8_t delay;
  uint8_t address;
  uint8_t length_write;
  uint8_t buffer_write[LONGEST_I2C_TRANSFER];
  uint8_t length_read;
  uint8_t buffer_read[LONGEST_I2C_TRANSFER];
};

// structure for custom sensors
struct sensor_custom_t{
  uint16_t adc1;
  uint16_t adc6;
  bool     pin5;
  bool     pin6;
};

// structure for touch sensors
struct sensor_touch_t{
  bool     pressed;
};

// structure for light sensor
struct sensor_light_t{
  int16_t  ambient;
  int16_t  reflected;
};

// structure for color sensors
struct sensor_color_t{
  int8_t   color;
  int16_t  reflected_red;
  int16_t  reflected_green;
  int16_t  reflected_blue;
  int16_t  ambient;
};

// structure for ultrasonic sensors
struct sensor_ultrasonic_t{
  float    cm;
  float    inch;
  bool     presence;
};

// structure for gyro sensor
struct sensor_gyro_t{
  int16_t  abs;
  int16_t  dps;
};

// structure for infrared sensor
struct sensor_infrared_t{
  uint8_t  proximity;
  int8_t   distance[4];
  int8_t   heading[4];
  uint8_t  remote[4];
};

// Set a BrickPi3's address to allow stacking
int BrickPi3_set_address(int addr, const char *id){
  if(addr < 1 || addr > 255){
    fatal_error("BrickPi3_set_address error: invalid address. Must be in the range of 1 to 255");
    return -1;
  }

  spi_array_out[0] = 0;                         // use address 0 so all BrickPi3s will listen, regardless of current address
  spi_array_out[1] = BPSPI_MESSAGE_SET_ADDRESS;
  spi_array_out[2] = addr;
  for(uint8_t i = 0; i < 16; i++){
    if(strlen(id) == 32){
      char id_str[2];
      id_str[0] = *(id + (i * 2));
      id_str[1] = *(id + (i * 2) + 1);
      spi_array_out[3 + i] = strtol(id_str, NULL, 16);
    }else if(strlen(id) == 0){
      spi_array_out[3 + i] = 0;
    }else{
      fatal_error("BrickPi3_set_address error: wrong serial number id length. Must be a 32-digit hex string.");
    }
  }
  if(spi_transfer_array(19, spi_array_out, spi_array_in)){
    return -1;
  }
  return 0;
}

class BrickPi3{
  public:
  // Default to address 1, but the BrickPi3 address could have been changed.
    BrickPi3(uint8_t addr = 1);

  // Confirm that the BrickPi3 is connected and up-to-date
    int     detect(bool critical = true);

  // Get the manufacturer (should be "Dexter Industries")
    int     get_manufacturer(char *str);
  // Get the board name (should be "BrickPi3")
    int     get_board(char *str);
  // Get the hardware version number
    int     get_version_hardware(char *str);
  // Get the firmware version number
    int     get_version_firmware(char *str);
  // Get the serial number ID that is unique to each BrickPi3
    int     get_id(char *str);
  // Control the LED
    int     set_led(uint8_t value);

  // Get the voltages of the four power rails
    // Get the voltage and return as floating point voltage
    float   get_voltage_3v3    ();
    float   get_voltage_5v     ();
    float   get_voltage_9v     ();
    float   get_voltage_battery();
    // Pass the pass-by-reference float variable where the voltage will be stored. Returns the error code.
    int     get_voltage_3v3    (float &voltage);
    int     get_voltage_5v     (float &voltage);
    int     get_voltage_9v     (float &voltage);
    int     get_voltage_battery(float &voltage);

  // Configure a sensor
    // Pass the port(s), sensor type, and optionally extra sensor configurations (flags and I2C information).
    int     set_sensor_type(uint8_t port, uint8_t type, uint16_t flags = 0, i2c_struct_t *i2c_struct = NULL);
  // Configure and trigger an I2C transaction
    int     transact_i2c(uint8_t port, i2c_struct_t *i2c_struct);
  // Get sensor value(s)
    int     get_sensor(uint8_t port, void *value_ptr);

  // Set the motor PWM power
    int     set_motor_power(uint8_t port, int8_t power);
  // Set the motor target position to run to
    // Set the absolute position to run to (go to the specified position)
    int     set_motor_position(uint8_t port, int32_t position);
    // Set the relative position to run to (go to the current position plus the specified position)
    int     set_motor_position_relative(uint8_t port, int32_t position);
  // Set the motor speed in degrees per second.
    int     set_motor_dps(uint8_t port, int16_t dps);
  // Set the motor limits.
  // Use the power limit to limit the motor speed/torque in speed or position control modes.
  // Use dps limit to limit the motor speed in position control mode.
    int     set_motor_limits(uint8_t port, uint8_t power, uint16_t dps);
  // Get the motor status. State, PWM power, encoder position, and speed (in degrees per second)
    int     get_motor_status(uint8_t port, uint8_t &state, int8_t &power, int32_t &position, int16_t &dps);
  // Offset the encoder position. By setting the offset to the current position, it effectively resets the encoder value.
    int     offset_motor_encoder(uint8_t port, int32_t position);
  // Reset the encoder.
    // Pass the port and pass-by-reference variable where the old encoder value will be stored. Returns the error code.
    int     reset_motor_encoder(uint8_t port, int32_t &value);
    // Pass the port. Returns the error code.
    int     reset_motor_encoder(uint8_t port);
  // Set the encoder position.
    // Pass the port and the new encoder position. Returns the error code.
    int     set_motor_encoder(uint8_t port, int32_t value);
  // Get the encoder position
    // Pass the port and pass-by-reference variable where the encoder value will be stored. Returns the error code.
    int     get_motor_encoder(uint8_t port, int32_t &value);
    // Pass the port. Returns the encoder value.
    int32_t get_motor_encoder(uint8_t port);

  // Reset the sensors (unconfigure), motors (float with no limits), and LED (return control to the firmware).
    int     reset_all();

  private:
    // BrickPi3 SPI address
    uint8_t Address;

    uint8_t SensorType[4];
    uint8_t I2CInBytes[4];

    int spi_file_handle = -1;                    // SPI file handle
    struct spi_ioc_transfer spi_xfer_struct;     // SPI transfer struct
    uint8_t spi_array_out[LONGEST_SPI_TRANSFER]; // SPI out array
    uint8_t spi_array_in[LONGEST_SPI_TRANSFER];  // SPI in array

    int spi_setup();
    int spi_transfer_array(uint8_t length, uint8_t *outArray, uint8_t *inArray);
    int BrickPi3_set_address(int addr, const char *id);

    void fatal_error(char *error);
    void fatal_error(const char *error);

    int spi_write_8(uint8_t msg_type, uint8_t value);
    int spi_read_16(uint8_t msg_type, uint16_t &value);
    int spi_read_32(uint8_t msg_type, uint32_t &value);
    int spi_read_string(uint8_t msg_type, char *str, uint8_t chars = 20);
};

#endif
