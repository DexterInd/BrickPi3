/*
 *  https://www.dexterindustries.com/BrickPi/
 *  https://github.com/DexterInd/BrickPi3
 *
 *  Copyright (c) 2017 Dexter Industries
 *  Released under the MIT license (http://choosealicense.com/licenses/mit/).
 *  For more information see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
 *
 *  C++ drivers for the BrickPi3
 */

#include "BrickPi3.h"

BrickPi3::BrickPi3(uint8_t addr){
  if(spi_file_handle < 0){
    if(spi_setup()){
      fatal_error("spi_setup error");
    }
  }
  
  if(addr < 1 || addr > 255){
    fatal_error("error: SPI address must be in the range of 1 to 255");
  }
  Address = addr;
}

int BrickPi3::spi_write_8(uint8_t msg_type, uint8_t value){
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  spi_array_out[2] = (value & 0xFF);
  return spi_transfer_array(3, spi_array_out, spi_array_in);
}

int BrickPi3::spi_read_16(uint8_t msg_type, uint16_t &value){
  value = 0;
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  if(int error = spi_transfer_array(6, spi_array_out, spi_array_in)){ // assign error to the value returned by spi_transfer_array, and if not 0:
    return error;
  }
  if(spi_array_in[3] != 0xA5){
    return ERROR_SPI_RESPONSE;
  }
  value = ((spi_array_in[4] << 8) | spi_array_in[5]);
  return ERROR_NONE;
}

int BrickPi3::spi_read_32(uint8_t msg_type, uint32_t &value){
  value = 0;
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  if(int error = spi_transfer_array(8, spi_array_out, spi_array_in)){ // assign error to the value returned by spi_transfer_array, and if not 0:
    return error;
  }
  if(spi_array_in[3] != 0xA5){
    return ERROR_SPI_RESPONSE;
  }
  value = ((spi_array_in[4] << 24) | (spi_array_in[5] << 16) | (spi_array_in[6] << 8) | spi_array_in[7]);
  return ERROR_NONE;
}

int BrickPi3::spi_read_string(uint8_t msg_type, char *str, uint8_t chars){
  if((chars + 4) > LONGEST_SPI_TRANSFER){
    return -3;
  }
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  if(int error = spi_transfer_array(chars + 4, spi_array_out, spi_array_in)){ // assign error to the value returned by spi_transfer_array, and if not 0:
    return error;
  }
  if(spi_array_in[3] != 0xA5){
    return ERROR_SPI_RESPONSE;
  }
  for(uint8_t i = 0; i < chars; i++){
    str[i] = spi_array_in[i + 4];
  }
  return ERROR_NONE;
}

int BrickPi3::detect(bool critical){
  char ErrorString[100];
  char string[21];
  int error;
  if(error = get_manufacturer(string)){     // assign error to the value returned by get_manufacturer, and if not 0:
    if(critical){
      fatal_error("detect error: get_manufacturer failed. Perhaps the BrickPi3 is not connected, or the address is incorrect.");
    }else{
      return error;
    }
  }
  if(strstr(string, "Dexter Industries") != string){
    if(critical){
      fatal_error("detect error: get_manufacturer string is not 'Dexter Industries'");
    }else{
      return ERROR_WRONG_MANUFACTURER;
    }
  }
  
  if(error = get_board(string)){            // assign error to the value returned by get_board, and if not 0:
    if(critical){
      fatal_error("detect error: get_board failed");
    }else{
      return error;
    }
  }
  if(strstr(string, "BrickPi3") != string){
    if(critical){
      fatal_error("detect error: get_board string is not 'BrickPi3'");
    }else{
      return ERROR_WRONG_DEVICE;
    }
  }
  
  if(error = get_version_firmware(string)){ // assign error to the value returned by get_version_firmware, and if not 0:
    if(critical){
      fatal_error("detect error: get_version_firmware failed");
    }else{
      return error;
    }
  }
  if(strstr(string, FIRMWARE_VERSION_REQUIRED) != string){
    if(critical){
      sprintf(ErrorString, "detect error: BrickPi3 firmware needs to be version %sx but is currently version %s", FIRMWARE_VERSION_REQUIRED, string);
      fatal_error(ErrorString);
    }else{
      return ERROR_FIRMWARE_MISMATCH;
    }
  }
  return ERROR_NONE;
}

int BrickPi3::get_manufacturer(char *str){
  str[0] = 0;
  return spi_read_string(BPSPI_MESSAGE_GET_MANUFACTURER, str);
}

int BrickPi3::get_board(char *str){
  str[0] = 0;
  return spi_read_string(BPSPI_MESSAGE_GET_NAME, str);
}

int BrickPi3::get_version_hardware(char *str){
  str[0] = 0;
  uint32_t value;
  if(int error = spi_read_32(BPSPI_MESSAGE_GET_HARDWARE_VERSION, value)){ // assign error to the value returned by spi_read_32, and if not 0:
    return error;
  }else{
    sprintf(str, "%d.%d.%d", (value / 1000000), ((value / 1000) % 1000), (value % 1000));
  }
}

int BrickPi3::get_version_firmware(char *str){
  str[0] = 0;
  uint32_t value;
  if(int error = spi_read_32(BPSPI_MESSAGE_GET_FIRMWARE_VERSION, value)){ // assign error to the value returned by spi_read_32, and if not 0:
    return error;
  }else{
    sprintf(str, "%d.%d.%d", (value / 1000000), ((value / 1000) % 1000), (value % 1000));
    return 0;
  }
}

int BrickPi3::get_id(char *str){
  str[0] = 0;
  spi_array_out[0] = Address;
  spi_array_out[1] = BPSPI_MESSAGE_GET_ID;
  if(spi_transfer_array(20, spi_array_out, spi_array_in)){
    return -1;
  }
  if(spi_array_in[3] != 0xA5){
    return -2;
  }
  for(int i = 0; i < 16; i++){
    sprintf((str + (i * 2)), "%02X", spi_array_in[i + 4]);
  }
}

void  BrickPi3::set_led(uint8_t value){
  spi_write_8(BPSPI_MESSAGE_SET_LED, value);
}

float BrickPi3::get_voltage_3v3(){
  uint16_t value;
  int res = spi_read_16(BPSPI_MESSAGE_GET_VOLTAGE_3V3, value);
  if(res){
    return res;
  }else{
    return value / 1000.0;
  }
}

float BrickPi3::get_voltage_5v(){
  uint16_t value;
  int res = spi_read_16(BPSPI_MESSAGE_GET_VOLTAGE_5V, value);
  if(res){
    return res;
  }else{
    return value / 1000.0;
  }
}

float BrickPi3::get_voltage_9v(){
  uint16_t value;
  int res = spi_read_16(BPSPI_MESSAGE_GET_VOLTAGE_9V, value);
  if(res){
    return res;
  }else{
    return value / 1000.0;
  }
}

float BrickPi3::get_voltage_battery(){
  uint16_t value;
  int res = spi_read_16(BPSPI_MESSAGE_GET_VOLTAGE_VCC, value);
  if(res){
    return res;
  }else{
    return value / 1000.0;
  }
}

int BrickPi3::set_sensor_type(uint8_t port, uint8_t type, uint16_t flags, i2c_struct_t *i2c_struct){
  for(uint8_t p = 0; p < 4; p++){
    if(port & (1 << p)){
      SensorType[p] = type;
    }
  }
  spi_array_out[0] = Address;
  spi_array_out[1] = BPSPI_MESSAGE_SET_SENSOR_TYPE;
  spi_array_out[2] = port;
  spi_array_out[3] = type;
  uint8_t spi_transfer_length = 4;
  
  if(type == SENSOR_TYPE_CUSTOM){
    spi_array_out[4] = ((flags >> 8) & 0xFF);
    spi_array_out[5] = (flags & 0xFF);
    spi_transfer_length = 6;
  }else if(type == SENSOR_TYPE_I2C){
    spi_array_out[4] = flags & 0xFF;
    spi_array_out[5] = i2c_struct->speed;
    if(flags & SENSOR_CONFIG_I2C_REPEAT){
      spi_array_out[6] = ((i2c_struct->delay >> 24) & 0xFF);
      spi_array_out[7] = ((i2c_struct->delay >> 16) & 0xFF);
      spi_array_out[8] = ((i2c_struct->delay >> 8) & 0xFF);
      spi_array_out[9] = (i2c_struct->delay & 0xFF);
      spi_array_out[10] = i2c_struct->address;
      if(i2c_struct->length_read > LONGEST_I2C_TRANSFER){
        i2c_struct->length_read = LONGEST_I2C_TRANSFER;
      }
      spi_array_out[11] = i2c_struct->length_read;
      for(uint8_t p = 0; p < 4; p++){
        if(port & (1 << p)){
          I2CInBytes[p] = i2c_struct->length_read;
        }
      }
      if(i2c_struct->length_write > LONGEST_I2C_TRANSFER){
        i2c_struct->length_write = LONGEST_I2C_TRANSFER;
      }
      spi_array_out[12] = i2c_struct->length_write;
      for(uint8_t i = 0; i < i2c_struct->length_write; i++){
        spi_array_out[13 + i] = i2c_struct->buffer_write[i];
      }
      spi_transfer_length = 13 + i2c_struct->length_write;
    }else{
      spi_transfer_length = 6;
    }
  }
  
  if(spi_transfer_array(spi_transfer_length, spi_array_out, spi_array_in)){
    return -1;
  }
  return 0;
}

int BrickPi3::transact_i2c(uint8_t port, i2c_struct_t *i2c_struct){
  uint8_t msg_type;
  switch(port){
    case PORT_1:
      msg_type = BPSPI_MESSAGE_I2C_TRANSACT_1;
    break;
    case PORT_2:
      msg_type = BPSPI_MESSAGE_I2C_TRANSACT_2;
    break;
    case PORT_3:
      msg_type = BPSPI_MESSAGE_I2C_TRANSACT_3;
    break;
    case PORT_4:
      msg_type = BPSPI_MESSAGE_I2C_TRANSACT_4;
    break;
    default:
      fatal_error("transact_i2c error. Must be one sensor port at a time. PORT_1, PORT_2, PORT_3, or PORT_4.");
  }
  
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  spi_array_out[2] = i2c_struct->address;
  
  if(i2c_struct->length_read > LONGEST_I2C_TRANSFER){
    i2c_struct->length_read = LONGEST_I2C_TRANSFER;
  }
  spi_array_out[3] = i2c_struct->length_read;
  for(uint8_t p = 0; p < 4; p++){
    if(port & (1 << p)){
      I2CInBytes[p] = i2c_struct->length_read;
    }
  }
  
  if(i2c_struct->length_write > LONGEST_I2C_TRANSFER){
    i2c_struct->length_write = LONGEST_I2C_TRANSFER;
  }
  spi_array_out[4] = i2c_struct->length_write;
  
  for(uint8_t i = 0; i < i2c_struct->length_write; i++){
    spi_array_out[5 + i] = i2c_struct->buffer_write[i];
  }
  
  if(spi_transfer_array((5 + i2c_struct->length_write), spi_array_out, spi_array_in)){
    return -1;
  }
  return 0;
}

int BrickPi3::get_sensor(uint8_t port, int32_t *value){
  uint8_t port_index;
  uint8_t msg_type;
  switch(port){
    case PORT_1:
      port_index = 0;
      msg_type = BPSPI_MESSAGE_GET_SENSOR_1;
    break;
    case PORT_2:
      port_index = 1;
      msg_type = BPSPI_MESSAGE_GET_SENSOR_2;
    break;
    case PORT_3:
      port_index = 2;
      msg_type = BPSPI_MESSAGE_GET_SENSOR_3;
    break;
    case PORT_4:
      port_index = 3;
      msg_type = BPSPI_MESSAGE_GET_SENSOR_4;
    break;
    default:
      fatal_error("get_sensor error. Must be one sensor port at a time. PORT_1, PORT_2, PORT_3, or PORT_4.");
  }
  
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  
  uint8_t spi_transfer_length;
  
  switch(SensorType[port_index]){
    case SENSOR_TYPE_TOUCH:
    case SENSOR_TYPE_TOUCH_NXT:
    case SENSOR_TYPE_TOUCH_EV3:
    case SENSOR_TYPE_NXT_ULTRASONIC:
    case SENSOR_TYPE_EV3_COLOR_REFLECTED:
    case SENSOR_TYPE_EV3_COLOR_AMBIENT:
    case SENSOR_TYPE_EV3_COLOR_COLOR:
    case SENSOR_TYPE_EV3_ULTRASONIC_LISTEN:
    case SENSOR_TYPE_EV3_INFRARED_PROXIMITY:
      spi_transfer_length = 7;
    break;
    case SENSOR_TYPE_NXT_LIGHT_ON:
    case SENSOR_TYPE_NXT_LIGHT_OFF:
    case SENSOR_TYPE_NXT_COLOR_RED:
    case SENSOR_TYPE_NXT_COLOR_GREEN:
    case SENSOR_TYPE_NXT_COLOR_BLUE:
    case SENSOR_TYPE_NXT_COLOR_OFF:
    case SENSOR_TYPE_EV3_GYRO_ABS:
    case SENSOR_TYPE_EV3_GYRO_DPS:
    case SENSOR_TYPE_EV3_ULTRASONIC_CM:
    case SENSOR_TYPE_EV3_ULTRASONIC_INCHES:
      spi_transfer_length = 8;
    break;
    case SENSOR_TYPE_CUSTOM:
    case SENSOR_TYPE_EV3_COLOR_RAW_REFLECTED:
    case SENSOR_TYPE_EV3_GYRO_ABS_DPS:
    case SENSOR_TYPE_EV3_INFRARED_REMOTE:
      spi_transfer_length = 10;
    break;
    case SENSOR_TYPE_NXT_COLOR_FULL:
      spi_transfer_length = 12;
    break;
    case SENSOR_TYPE_EV3_COLOR_COLOR_COMPONENTS:
    case SENSOR_TYPE_EV3_INFRARED_SEEK:
      spi_transfer_length = 14;
    break;
    case SENSOR_TYPE_I2C:
      spi_transfer_length = 6 + I2CInBytes[port_index];
    break;
    
    // Invalid or unsupported sensor type
    default:
      return SENSOR_STATE_NOT_CONFIGURED;
    break;
  }
  
  if(int error = spi_transfer_array(spi_transfer_length, spi_array_out, spi_array_in)){
    return error;
  }
  if(spi_array_in[3] != 0xA5){
    return ERROR_SPI_RESPONSE;
  }
  if(!(spi_array_in[4] == SensorType[port_index] || (SensorType[port_index] == SENSOR_TYPE_TOUCH && (spi_array_in[4] == SENSOR_TYPE_TOUCH_NXT || spi_array_in[4] == SENSOR_TYPE_TOUCH_EV3)))){
    return ERROR_SENSOR_TYPE_MISMATCH;
  }
  if(spi_array_in[5] != SENSOR_STATE_VALID_DATA){
    return spi_array_in[5];
  }
  
  switch(SensorType[port_index]){
    case SENSOR_TYPE_TOUCH:
    case SENSOR_TYPE_TOUCH_NXT:
    case SENSOR_TYPE_TOUCH_EV3:
    case SENSOR_TYPE_NXT_ULTRASONIC:
    case SENSOR_TYPE_EV3_COLOR_REFLECTED:
    case SENSOR_TYPE_EV3_COLOR_AMBIENT:
    case SENSOR_TYPE_EV3_COLOR_COLOR:
    case SENSOR_TYPE_EV3_ULTRASONIC_LISTEN:
    case SENSOR_TYPE_EV3_INFRARED_PROXIMITY:
      *value = spi_array_in[6];
    break;
    case SENSOR_TYPE_NXT_LIGHT_ON:
    case SENSOR_TYPE_NXT_LIGHT_OFF:
    case SENSOR_TYPE_NXT_COLOR_RED:
    case SENSOR_TYPE_NXT_COLOR_GREEN:
    case SENSOR_TYPE_NXT_COLOR_BLUE:
    case SENSOR_TYPE_NXT_COLOR_OFF:
    case SENSOR_TYPE_EV3_GYRO_ABS:
    case SENSOR_TYPE_EV3_GYRO_DPS:
    case SENSOR_TYPE_EV3_ULTRASONIC_CM:
    case SENSOR_TYPE_EV3_ULTRASONIC_INCHES:
      *value = ((spi_array_in[6] << 8) | spi_array_in[7]);
      switch(SensorType[port_index]){
        case SENSOR_TYPE_EV3_GYRO_ABS:
        case SENSOR_TYPE_EV3_GYRO_DPS:
          if(*value & 0x8000){
            *value -= 0x10000;
          }
        break;
        /*case SENSOR_TYPE_EV3_ULTRASONIC_CM:
        case SENSOR_TYPE_EV3_ULTRASONIC_INCHES:
          *value = *value / 10; // divide by 10 to get CM and Inches
        break;*/
      }
    break;
    case SENSOR_TYPE_CUSTOM:
      *value       = (((spi_array_in[8] & 0x0F) << 8) | spi_array_in[9]);
      *(value + 1) = (((spi_array_in[8] >> 4) & 0x0F) | (spi_array_in[7] << 4));
      *(value + 2) = (spi_array_in[6] & 0x01);
      *(value + 3) = ((spi_array_in[6] >> 1) & 0x01);
    break;
    case SENSOR_TYPE_EV3_COLOR_RAW_REFLECTED:
    case SENSOR_TYPE_EV3_GYRO_ABS_DPS:
      *value       = ((spi_array_in[6] << 8) | spi_array_in[7]);
      *(value + 1) = ((spi_array_in[8] << 8) | spi_array_in[9]);
      if(SensorType[port_index] == SENSOR_TYPE_EV3_GYRO_ABS_DPS){
        if(*value & 0x8000){
          *value -= 0x10000;
        }
        if(*(value + 1) & 0x8000){
          *(value + 1) -= 0x10000;
        }
      }
    break;
    case SENSOR_TYPE_EV3_INFRARED_REMOTE:
      for(uint8_t v = 0; v < 4; v++){
        switch(spi_array_in[6 + v]){
          case 1:
            *(value + v) = REMOTE_BIT_RED_UP;
          break;
          case 2:
            *(value + v) = REMOTE_BIT_RED_DOWN;
          break;
          case 3:
            *(value + v) = REMOTE_BIT_BLUE_UP;
          break;
          case 4:
            *(value + v) = REMOTE_BIT_BLUE_DOWN;
          break;
          case 5:
            *(value + v) = REMOTE_BIT_RED_UP | REMOTE_BIT_BLUE_UP;
          break;
          case 6:
            *(value + v) = REMOTE_BIT_RED_UP | REMOTE_BIT_BLUE_DOWN;
          break;
          case 7:
            *(value + v) = REMOTE_BIT_RED_DOWN | REMOTE_BIT_BLUE_UP;
          break;
          case 8:
            *(value + v) = REMOTE_BIT_RED_DOWN | REMOTE_BIT_BLUE_DOWN;
          break;
          case 9:
            *(value + v) = REMOTE_BIT_BROADCAST;
          break;
          case 10:
            *(value + v) = REMOTE_BIT_RED_UP | REMOTE_BIT_RED_DOWN;
          break;
          case 11:
            *(value + v) = REMOTE_BIT_BLUE_UP | REMOTE_BIT_BLUE_DOWN;
          break;
          default:
            *(value + v) = 0;
          break;
        }
      }
    break;
    case SENSOR_TYPE_NXT_COLOR_FULL:
      *value       = spi_array_in[6];
      *(value + 1) = ((spi_array_in[ 7] << 2) | ((spi_array_in[11] >> 6) & 0x03));
      *(value + 2) = ((spi_array_in[ 8] << 2) | ((spi_array_in[11] >> 4) & 0x03));
      *(value + 3) = ((spi_array_in[ 9] << 2) | ((spi_array_in[11] >> 2) & 0x03));
      *(value + 4) = ((spi_array_in[10] << 2) | ( spi_array_in[11]       & 0x03));
    break;
    case SENSOR_TYPE_EV3_COLOR_COLOR_COMPONENTS:
      *value       = ((spi_array_in[ 6] << 8) | spi_array_in[ 7]);
      *(value + 1) = ((spi_array_in[ 8] << 8) | spi_array_in[ 9]);
      *(value + 2) = ((spi_array_in[10] << 8) | spi_array_in[11]);
      *(value + 3) = ((spi_array_in[12] << 8) | spi_array_in[13]);
    break;
    case SENSOR_TYPE_EV3_INFRARED_SEEK:
      *value       = spi_array_in[ 6];
      *(value + 1) = spi_array_in[ 7];
      *(value + 2) = spi_array_in[ 8];
      *(value + 3) = spi_array_in[ 9];
      *(value + 4) = spi_array_in[10];
      *(value + 5) = spi_array_in[11];
      *(value + 6) = spi_array_in[12];
      *(value + 7) = spi_array_in[13];
      for(uint8_t v = 0; v < 8; v++){
        if(*(value + v) & 0x80){
          *(value + v) -= 0x100;
        }
      }
    break;
    case SENSOR_TYPE_I2C:
      for(uint8_t b = 0; b < I2CInBytes[port_index]; b++){
        *(value + b) = spi_array_in[6 + b];
      }
    break;
  }
  return SENSOR_STATE_VALID_DATA;
}

int BrickPi3::set_motor_power(uint8_t port, int8_t power){
  spi_array_out[0] = Address;
  spi_array_out[1] = BPSPI_MESSAGE_SET_MOTOR_POWER;
  spi_array_out[2] = port;
  spi_array_out[3] = power;
  if(spi_transfer_array(4, spi_array_out, spi_array_in)){
    return -1;
  }
  return 0;
}
    
int BrickPi3::set_motor_position(uint8_t port, int32_t position){
  spi_array_out[0] = Address;
  spi_array_out[1] = BPSPI_MESSAGE_SET_MOTOR_POSITION;
  spi_array_out[2] = port;
  spi_array_out[3] = ((position >> 24) & 0xFF);
  spi_array_out[4] = ((position >> 16) & 0xFF);
  spi_array_out[5] = ((position >> 8) & 0xFF);
  spi_array_out[6] = (position & 0xFF);
  if(spi_transfer_array(7, spi_array_out, spi_array_in)){
    return -1;
  }
  return 0;
}
    
int BrickPi3::set_motor_dps(uint8_t port, int16_t dps){
  spi_array_out[0] = Address;
  spi_array_out[1] = BPSPI_MESSAGE_SET_MOTOR_DPS;
  spi_array_out[2] = port;
  spi_array_out[3] = ((dps >> 8) & 0xFF);
  spi_array_out[4] = (dps & 0xFF);
  if(spi_transfer_array(5, spi_array_out, spi_array_in)){
    return -1;
  }
  return 0;
}
    
int BrickPi3::set_motor_limits(uint8_t port, uint8_t power, uint16_t dps){
  spi_array_out[0] = Address;
  spi_array_out[1] = BPSPI_MESSAGE_SET_MOTOR_LIMITS;
  spi_array_out[2] = port;
  spi_array_out[3] = power;
  spi_array_out[4] = ((dps >> 8) & 0xFF);
  spi_array_out[5] = (dps & 0xFF);
  if(spi_transfer_array(6, spi_array_out, spi_array_in)){
    return -1;
  }
  return 0;
}

int BrickPi3::get_motor_status(uint8_t port, uint8_t &state, int8_t &power, int32_t &position, int16_t &dps){
  uint8_t msg_type;
  switch(port){
    case PORT_A:
      msg_type = BPSPI_MESSAGE_GET_MOTOR_A_STATUS;
    break;
    case PORT_B:
      msg_type = BPSPI_MESSAGE_GET_MOTOR_B_STATUS;
    break;
    case PORT_C:
      msg_type = BPSPI_MESSAGE_GET_MOTOR_C_STATUS;
    break;
    case PORT_D:
      msg_type = BPSPI_MESSAGE_GET_MOTOR_D_STATUS;
    break;
    default:
      fatal_error("get_motor_encoder error. Must be one motor port at a time. PORT_A, PORT_B, PORT_C, or PORT_D.");
  }
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  if(spi_transfer_array(12, spi_array_out, spi_array_in)){
    return -1;
  }
  if(spi_array_in[3] != 0xA5){
    return -2;
  }
  
  state    = spi_array_in[4];
  power    = spi_array_in[5];
  position = ((spi_array_in[6] << 24) | (spi_array_in[7] << 16) | (spi_array_in[8] << 8) | spi_array_in[9]);
  dps      = ((spi_array_in[10] << 8) | spi_array_in[11]);
  
  return 0;
}

int BrickPi3::offset_motor_encoder(uint8_t port, int32_t position){
  spi_array_out[0] = Address;
  spi_array_out[1] = BPSPI_MESSAGE_OFFSET_MOTOR_ENCODER;
  spi_array_out[2] = port;
  spi_array_out[3] = ((position >> 24) & 0xFF);
  spi_array_out[4] = ((position >> 16) & 0xFF);
  spi_array_out[5] = ((position >> 8) & 0xFF);
  spi_array_out[6] = (position & 0xFF);
  if(spi_transfer_array(7, spi_array_out, spi_array_in)){
    return -1;
  }
  return 0;
}

int32_t BrickPi3::get_motor_encoder(uint8_t port){
  uint8_t msg_type;
  switch(port){
    case PORT_A:
      msg_type = BPSPI_MESSAGE_GET_MOTOR_A_ENCODER;
    break;
    case PORT_B:
      msg_type = BPSPI_MESSAGE_GET_MOTOR_B_ENCODER;
    break;
    case PORT_C:
      msg_type = BPSPI_MESSAGE_GET_MOTOR_C_ENCODER;
    break;
    case PORT_D:
      msg_type = BPSPI_MESSAGE_GET_MOTOR_D_ENCODER;
    break;
    default:
      fatal_error("get_motor_encoder error. Must be one motor port at a time. PORT_A, PORT_B, PORT_C, or PORT_D.");
  }
  
  uint32_t value;
  spi_read_32(msg_type, value);
  return value;
}

void BrickPi3::reset_all(){
    set_sensor_type(PORT_1 + PORT_2 + PORT_3 + PORT_4, SENSOR_TYPE_NONE);
    set_motor_power(PORT_A + PORT_B + PORT_C + PORT_D, MOTOR_FLOAT);
    set_led(-1);
}
