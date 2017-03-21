# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# Python drivers for the BrickPi3

from __future__ import print_function
from __future__ import division
#from builtins import input

import subprocess # for executing system calls
import spidev

FIRMWARE_VERSION_REQUIRED = "1.3.x" # Make sure the top 2 of 3 numbers match

BP_SPI = spidev.SpiDev()
BP_SPI.open(0, 1)
BP_SPI.max_speed_hz = 500000 #1000000 #1300000
BP_SPI.mode = 0b00
BP_SPI.bits_per_word = 8
#BP_SPI.delay_usec = 10

class Enumeration(object):
    def __init__(self, names):  # or *names, with no .split()
        number = 0
        for line, name in enumerate(names.split('\n')):
            if name.find(",") >= 0:
                # strip out the spaces
                while(name.find(" ") != -1):
                    name = name[:name.find(" ")] + name[(name.find(" ") + 1):]
                
                # strip out the commas
                while(name.find(",") != -1):
                    name = name[:name.find(",")] + name[(name.find(",") + 1):]
                
                # if the value was specified
                if(name.find("=") != -1):
                    number = int(float(name[(name.find("=") + 1):]))
                    name = name[:name.find("=")]
                
                # optionally print to confirm that it's working correctly
                #print "%40s has a value of %d" % (name, number)
                
                setattr(self, name, number)
                number = number + 1

class FirmwareVersionError(Exception):
    """Exception raised if the BrickPi3 firmware needs to be updated"""

class BrickPi3(object):
    PORT_1 = 0
    PORT_2 = 1
    PORT_3 = 2
    PORT_4 = 3
    
    PORT_A = 0
    PORT_B = 1
    PORT_C = 2
    PORT_D = 3
    
    SensorType = [0, 0, 0, 0]
    I2CInBytes = [0, 0, 0, 0]
    
    BPSPI_MESSAGE_TYPE = Enumeration("""
        NONE,
        
        READ_MANUFACTURER,
        READ_NAME,
        READ_HARDWARE_VERSION,
        READ_FIRMWARE_VERSION,
        READ_ID,
        SET_LED,
        READ_VOLTAGE_3V3,
        READ_VOLTAGE_5V,
        READ_VOLTAGE_9V,
        READ_VOLTAGE_VCC,
        
        SET_SENSOR_TYPE = 20,
        SET_SENSOR_1_TYPE = 20,
        SET_SENSOR_2_TYPE,
        SET_SENSOR_3_TYPE,
        SET_SENSOR_4_TYPE,
        
        READ_SENSOR = 24,
        READ_SENSOR_1 = 24,
        READ_SENSOR_2,
        READ_SENSOR_3,
        READ_SENSOR_4,
        
        WRITE_MOTOR_POWER = 28,
        WRITE_MOTOR_A_POWER = 28,
        WRITE_MOTOR_B_POWER,
        WRITE_MOTOR_C_POWER,
        WRITE_MOTOR_D_POWER,
        
        WRITE_MOTOR_POSITION = 32,
        WRITE_MOTOR_A_POSITION = 32,
        WRITE_MOTOR_B_POSITION,
        WRITE_MOTOR_C_POSITION,
        WRITE_MOTOR_D_POSITION,
        
        WRITE_MOTOR_POSITION_KP = 36,
        WRITE_MOTOR_A_POSITION_KP = 36,
        WRITE_MOTOR_B_POSITION_KP,
        WRITE_MOTOR_C_POSITION_KP,
        WRITE_MOTOR_D_POSITION_KP,
        
        WRITE_MOTOR_POSITION_KD = 40,
        WRITE_MOTOR_A_POSITION_KD = 40,
        WRITE_MOTOR_B_POSITION_KD,
        WRITE_MOTOR_C_POSITION_KD,
        WRITE_MOTOR_D_POSITION_KD,
        
        WRITE_MOTOR_DPS = 44,
        WRITE_MOTOR_A_DPS = 44,
        WRITE_MOTOR_B_DPS,
        WRITE_MOTOR_C_DPS,
        WRITE_MOTOR_D_DPS,
        
        WRITE_MOTOR_DPS_KP = 48,
        WRITE_MOTOR_A_DPS_KP = 48,
        WRITE_MOTOR_B_DPS_KP,
        WRITE_MOTOR_C_DPS_KP,
        WRITE_MOTOR_D_DPS_KP,
        
        WRITE_MOTOR_DPS_KD = 52,
        WRITE_MOTOR_A_DPS_KD = 52,
        WRITE_MOTOR_B_DPS_KD,
        WRITE_MOTOR_C_DPS_KD,
        WRITE_MOTOR_D_DPS_KD,
        
        OFFSET_MOTOR_ENCODER = 56,
        OFFSET_MOTOR_A_ENCODER = 56,
        OFFSET_MOTOR_B_ENCODER,
        OFFSET_MOTOR_C_ENCODER,
        OFFSET_MOTOR_D_ENCODER,
        
        READ_MOTOR_ENCODER = 60,
        READ_MOTOR_A_ENCODER = 60,
        READ_MOTOR_B_ENCODER,
        READ_MOTOR_C_ENCODER,
        READ_MOTOR_D_ENCODER,
        
        I2C_TRANSACT = 64,
        I2C_TRANSACT_1 = 64,
        I2C_TRANSACT_2,
        I2C_TRANSACT_3,
        I2C_TRANSACT_4,
        
        WRITE_MOTOR_LIMITS = 68,
        WRITE_MOTOR_A_LIMITS = 68,
        WRITE_MOTOR_B_LIMITS,
        WRITE_MOTOR_C_LIMITS,
        WRITE_MOTOR_D_LIMITS,
        
        READ_MOTOR_STATUS = 72,
        READ_MOTOR_A_STATUS = 72,
        READ_MOTOR_B_STATUS,
        READ_MOTOR_C_STATUS,
        READ_MOTOR_D_STATUS,
    """)
    
    SENSOR_TYPE = Enumeration("""
        NONE = 1,
        I2C,
        CUSTOM,
        
        TOUCH,
        NXT_TOUCH,
        EV3_TOUCH,
        
        NXT_LIGHT_ON,
        NXT_LIGHT_OFF,
        
        NXT_COLOR_RED,
        NXT_COLOR_GREEN,
        NXT_COLOR_BLUE,
        NXT_COLOR_FULL,
        NXT_COLOR_OFF,
        
        NXT_ULTRASONIC,
        
        EV3_GYRO_ABS,
        EV3_GYRO_DPS,
        EV3_GYRO_ABS_DPS,
        
        EV3_COLOR_REFLECTED,
        EV3_COLOR_AMBIENT,
        EV3_COLOR_COLOR,
        EV3_COLOR_RAW_REFLECTED,
        EV3_COLOR_COLOR_COMPONENTS,
        
        EV3_ULTRASONIC_CM,
        EV3_ULTRASONIC_INCHES,
        EV3_ULTRASONIC_LISTEN,
        
        EV3_INFRARED_PROXIMITY,
        EV3_INFRARED_SEEK,
        EV3_INFRARED_REMOTE,
    """)
    
    SENSOR_STATE = Enumeration("""
        VALID_DATA,
        NOT_CONFIGURED,
        CONFIGURING,
        NO_DATA,
    """)
    
    SENSOR_CUSTOM = Enumeration("""
        PIN1_9V,
        PIN5_OUT,
        PIN5_STATE,
        PIN6_OUT,
        PIN6_STATE,
        PIN1_ADC,
        PIN6_ADC,
    """)
    
    SENSOR_CUSTOM.PIN1_9V    = 0x0002
    SENSOR_CUSTOM.PIN5_OUT   = 0x0010
    SENSOR_CUSTOM.PIN5_STATE = 0x0020
    SENSOR_CUSTOM.PIN6_OUT   = 0x0100
    SENSOR_CUSTOM.PIN6_STATE = 0x0200
    SENSOR_CUSTOM.PIN1_ADC   = 0x1000
    SENSOR_CUSTOM.PIN6_ADC   = 0x4000
    
    SENSOR_I2C_SETTINGS = Enumeration("""
        MID_CLOCK,
        PIN1_9V,
        SAME,
        ALLOW_STRETCH_ACK,
        ALLOW_STRETCH_ANY,
    """)
    
    SENSOR_I2C_SETTINGS.MID_CLOCK         = 0x01 # Send the clock pulse between reading and writing. Required by the NXT US sensor.
    SENSOR_I2C_SETTINGS.PIN1_9V           = 0x02 # 9v pullup on pin 1
    SENSOR_I2C_SETTINGS.SAME              = 0x04 # Keep performing the same transaction e.g. keep polling a sensor
    
    MOTOR_STATUS_FLAG = Enumeration("""
        LOW_VOLTAGE_FLOAT,
    """)
    
    MOTOR_STATUS_FLAG.LOW_VOLTAGE_FLOAT = 0x01 # If the motors are floating due to low battery voltage
    
    SUCCESS = 0
    SPI_ERROR = 1
    SENSOR_ERROR = 2
    SENSOR_TYPE_ERROR = 3
    
    def __init__(self, addr = 1, detect = True): # Configure for the BrickPi. Optionally set the address (default to 1).
        """
        Do any necessary configuration, and optionally detect the BrickPi3
        
        Optionally set the SPI address to something other than 1
        """
        
        # note these two lines were a temporary work-around for older Raspbian For Robots.
        subprocess.call('gpio mode 13 ALT0', shell=True) # Make sure the SPI lines are configured for mode ALT0 so that the hardware SPI controller can use them
        subprocess.call('gpio mode 14 ALT0', shell=True) #                                                  ''
        
        self.SPI_Address = addr
        if detect == True:
            manufacturer, merr = self.get_manufacturer()
            board, berr = self.get_board()
            vfw, verr = self.get_version_firmware()
            if merr != self.SUCCESS or berr != self.SUCCESS or verr != self.SUCCESS or manufacturer != "Dexter Industries" or board != "BrickPi3":
                raise IOError("BrickPi3 not connected")
            if vfw.split('.')[0] != FIRMWARE_VERSION_REQUIRED.split('.')[0] or vfw.split('.')[1] != FIRMWARE_VERSION_REQUIRED.split('.')[1]:
                raise FirmwareVersionError("BrickPi3 firmware needs to be version %s but is currently version %s" % (FIRMWARE_VERSION_REQUIRED, vfw))
    
    def spi_transfer_array(self, data_out):
        """
        Conduct a SPI transaction
        
        Keyword arguments:
        data_out -- a list of bytes to send. The length of the list will determine how many bytes are transferred.
        
        Returns a list of the bytes read.
        """
        return BP_SPI.xfer2(data_out)
    
#    def spi_read_8(self, MessageType):
#        """
#        Read an 8-bit value over SPI
#        
#        Keyword arguments:
#        MessageType -- the SPI message type
#        
#        Returns touple:
#            value, error
#        """
#        outArray = [self.SPI_Address, MessageType, 0, 0, 0]
#        reply = self.spi_transfer_array(outArray)
#        if(reply[3] == 0xA5):
#            return int((reply[4] & 0xFF)), self.SUCCESS
#        return 0, self.SPI_ERROR
    
    def spi_write_8(self, MessageType, Value):
        """
        Send an 8-bit value over SPI
        
        Keyword arguments:
        MessageType -- the SPI message type
        Value -- the value to be sent
        """
        outArray = [self.SPI_Address, MessageType, (Value & 0xFF)]
        self.spi_transfer_array(outArray)
    
    def spi_read_16(self, MessageType):
        """
        Read a 16-bit value over SPI
        
        Keyword arguments:
        MessageType -- the SPI message type
        
        Returns touple:
        value, error
        """
        outArray = [self.SPI_Address, MessageType, 0, 0, 0, 0]
        reply = self.spi_transfer_array(outArray)
        if(reply[3] == 0xA5):
            return int((reply[4] << 8) | reply[5]), self.SUCCESS
        return 0, self.SPI_ERROR
    
    def spi_write_16(self, MessageType, Value):
        """
        Send a 16-bit value over SPI
        
        Keyword arguments:
        MessageType -- the SPI message type
        Value -- the value to be sent
        """
        outArray = [self.SPI_Address, MessageType, ((Value >> 8) & 0xFF), (Value & 0xFF)]
        self.spi_transfer_array(outArray)
    
    def spi_write_24(self, MessageType, Value):
        """
        Send a 24-bit value over SPI
        
        Keyword arguments:
        MessageType -- the SPI message type
        Value -- the value to be sent
        """
        outArray = [self.SPI_Address, MessageType, ((Value >> 16) & 0xFF), ((Value >> 8) & 0xFF), (Value & 0xFF)]
        self.spi_transfer_array(outArray)
    
    def spi_read_32(self, MessageType):
        """
        Read a 32-bit value over SPI
        
        Keyword arguments:
        MessageType -- the SPI message type
        
        Returns touple:
        value, error
        """
        outArray = [self.SPI_Address, MessageType, 0, 0, 0, 0, 0, 0]
        reply = self.spi_transfer_array(outArray)
        if(reply[3] == 0xA5):
            return int((reply[4] << 24) | (reply[5] << 16) | (reply[6] << 8) | reply[7]), self.SUCCESS
        return 0, self.SPI_ERROR
    
    def spi_write_32(self, MessageType, Value):
        """
        Send a 32-bit value over SPI
        
        Keyword arguments:
        MessageType -- the SPI message type
        Value -- the value to be sent
        """
        outArray = [self.SPI_Address, MessageType, ((Value >> 24) & 0xFF), ((Value >> 16) & 0xFF), ((Value >> 8) & 0xFF), (Value & 0xFF)]
        self.spi_transfer_array(outArray)
    
    def get_manufacturer(self):
        """
        Read the 20 charactor BrickPi3 manufacturer name
        
        Returns touple:
        BrickPi3 manufacturer name string, error
        """
        outArray = [self.SPI_Address, self.BPSPI_MESSAGE_TYPE.READ_MANUFACTURER, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        reply = self.spi_transfer_array(outArray)
        if(reply[3] == 0xA5):
            name = ""
            for c in range(4, 24):
                if reply[c] != 0:
                    name += chr(reply[c])
                else:
                    break
            return name, self.SUCCESS
        return "", self.SPI_ERROR
    
    def get_board(self):
        """
        Read the 20 charactor BrickPi3 board name
        
        Returns touple:
        BrickPi3 board name string, error
        """
        outArray = [self.SPI_Address, self.BPSPI_MESSAGE_TYPE.READ_NAME, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        reply = self.spi_transfer_array(outArray)
        if(reply[3] == 0xA5):
            name = ""
            for c in range(4, 24):
                if reply[c] != 0:
                    name += chr(reply[c])
                else:
                    break
            return name, self.SUCCESS
        return "", self.SPI_ERROR
    
    def get_version_hardware(self):
        """
        Read the hardware version
        
        Returns touple:
        hardware version, error
        """
        version, error = self.spi_read_32(self.BPSPI_MESSAGE_TYPE.READ_HARDWARE_VERSION)
        return ("%d.%d.%d" % ((version / 1000000), ((version / 1000) % 1000), (version % 1000))), error
    
    def get_version_firmware(self):
        """
        Read the firmware version
        
        Returns touple:
        firmware version, error
        """
        version, error = self.spi_read_32(self.BPSPI_MESSAGE_TYPE.READ_FIRMWARE_VERSION)
        return ("%d.%d.%d" % ((version / 1000000), ((version / 1000) % 1000), (version % 1000))), error
    
    def get_id(self):
        """
        Read the 128-bit BrickPi hardware serial number
        
        Returns touple:
        serial number as 32 char HEX formatted string, error
        """
        outArray = [self.SPI_Address, self.BPSPI_MESSAGE_TYPE.READ_ID, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        reply = self.spi_transfer_array(outArray)
        if(reply[3] == 0xA5):
            return ("%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X" % (reply[4], reply[5], reply[6], reply[7], reply[8], reply[9], reply[10], reply[11], reply[12], reply[13], reply[14], reply[15], reply[16], reply[17], reply[18], reply[19])), self.SUCCESS
        return "00000000000000000000000000000000", self.SPI_ERROR
    
    def set_led(self, value):
        """
        Control the onboard LED
        
        Keyword arguments:
        value -- the value (in percent) to set the LED brightness to. -1 returns control of the LED to the firmware.
        """
        self.spi_write_8(self.BPSPI_MESSAGE_TYPE.SET_LED, value)
    
    def get_voltage_3v3(self):
        """
        Get the 3.3v circuit voltage
        
        Returns touple:
        3.3v circuit voltage, error
        """
        value, error = self.spi_read_16(self.BPSPI_MESSAGE_TYPE.READ_VOLTAGE_3V3)
        return (value / 1000.0), error
    
    def get_voltage_5v(self):
        """
        Get the 5v circuit voltage
        
        Returns touple:
        5v circuit voltage, error
        """
        value, error = self.spi_read_16(self.BPSPI_MESSAGE_TYPE.READ_VOLTAGE_5V)
        return (value / 1000.0), error
    
    def get_voltage_9v(self):
        """
        Get the 9v circuit voltage
        
        Returns touple:
        9v circuit voltage, error
        """
        value, error = self.spi_read_16(self.BPSPI_MESSAGE_TYPE.READ_VOLTAGE_9V)
        return (value / 1000.0), error
    
    def get_voltage_battery(self):
        """
        Get the battery voltage
        
        Returns touple:
        battery voltage, error
        """
        value, error = self.spi_read_16(self.BPSPI_MESSAGE_TYPE.READ_VOLTAGE_VCC)
        return (value / 1000.0), error
    
    def set_sensor_type(self, port, type, params = 0):
        """
        Set the sensor type
        
        Keyword arguments:
        port -- The sensor port
        type -- The sensor type
        params = 0 -- the parameters needed for some sensor types.
        
        params is used for the following sensor types:
            CUSTOM -- a 24-bit integer used to configure the hardware.
            I2C -- a list of settings:
                params[0] -- Settings/flags
                params[1] -- target Speed in microseconds (0-255). Realistically the speed will vary.
                if SENSOR_I2C_SETTINGS_SAME flag set in I2C Settings:
                    params[2] -- Delay in microseconds between transactions.
                    params[3] -- Address
                    params[4] -- List of bytes to write
                    params[5] -- Number of bytes to read
        """
        self.SensorType[port] = type
        if(type == self.SENSOR_TYPE.CUSTOM):
            self.spi_write_24((self.BPSPI_MESSAGE_TYPE.SET_SENSOR_TYPE + port), ((type << 16) + (params[0])))
        elif(type == self.SENSOR_TYPE.I2C):
            if len(params) >= 2:
                outArray = [self.SPI_Address, (self.BPSPI_MESSAGE_TYPE.SET_SENSOR_TYPE + port), type, params[0], params[1]] # Settings, SpeedUS
                if params[0] & self.SENSOR_I2C_SETTINGS.SAME and len(params) >= 6:
                    outArray.append((params[2] >> 24) & 0xFF) # DelayUS
                    outArray.append((params[2] >> 16) & 0xFF) #   ''
                    outArray.append((params[2] >> 8) & 0xFF)  #   ''
                    outArray.append(params[2] & 0xFF)         #   '' 
                    outArray.append(params[3] & 0xFF)   # Address
                    outArray.append(params[5] & 0xFF)   # InBytes
                    self.I2CInBytes[port] = params[5] & 0xFF
                    outArray.append(len(params[4]))     # OutBytes
                    outArray.extend(params[4])          # OutArray
                self.spi_transfer_array(outArray)
        else:
            self.spi_write_8((self.BPSPI_MESSAGE_TYPE.SET_SENSOR_TYPE + port), type)
    
#    def check_sensor_type(self, port):
#        """
#        Check the sensor type
#        
#        Keyword arguments:
#        port -- The sensor port
#        
#        Returns:
#        type -- The sensor type
#        """
#        return self.SensorType[port]
    
    def transact_i2c(self, port, Address, OutArray, InBytes):
        """
        Conduct an I2C transaction
        
        Keyword arguments:
        port -- The sensor port
        Address -- The I2C address for the device. Bits 1-7, not 0-6.
        OutArray -- A list of bytes to write to the device
        InBytes -- The number of bytes to read from the device
        """
        if self.SensorType[port] != self.SENSOR_TYPE.I2C:
            return
        outArray = [self.SPI_Address, (self.BPSPI_MESSAGE_TYPE.I2C_TRANSACT + port), Address, InBytes]
        self.I2CInBytes[port] = InBytes
        OutBytes = len(OutArray)
        if(OutBytes > 16):
            outArray.append(16)
            for b in range(16):
                outArray.append(OutArray[b])
        else:
            outArray.append(OutBytes)
            outArray.extend(OutArray)
        self.spi_transfer_array(outArray)
    
    def get_sensor(self, port):
        """
        Read a sensor value
        
        Keyword arguments:
        port -- The sensor port.
        
        Returns a touple with the value(s) for the specified sensor, and the read error.
            The following sensor types each return a single value:
                NONE ----------------------- 0
                TOUCH ---------------------- 0 or 1 (released or pressed)
                NXT_TOUCH ------------------ 0 or 1 (released or pressed)
                EV3_TOUCH ------------------ 0 or 1 (released or pressed)
                NXT_ULTRASONIC ------------- distance in CM
                NXT_LIGHT_ON  -------------- reflected light
                NXT_LIGHT_OFF -------------- ambient light
                NXT_COLOR_RED -------------- red reflected light
                NXT_COLOR_GREEN ------------ green reflected light
                NXT_COLOR_BLUE ------------- blue reflected light
                NXT_COLOR_OFF -------------- ambient light
                EV3_GYRO_ABS --------------- absolute rotation position in degrees
                EV3_GYRO_DPS --------------- rotation rate in degrees per second
                EV3_COLOR_REFLECTED -------- red reflected light
                EV3_COLOR_AMBIENT ---------- ambient light
                EV3_COLOR_COLOR ------------ detected color
                EV3_ULTRASONIC_CM ---------- distance in CM
                EV3_ULTRASONIC_INCHES ------ distance in inches
                EV3_ULTRASONIC_LISTEN ------ 0 or 1 (no other ultrasonic sensors or another ultrasonic sensor detected)
                EV3_INFRARED_PROXIMITY ----- distance 0-100%
            
            The following sensor types each return a list of values
                CUSTOM --------------------- Pin 1 ADC (5v scale from 0 to 4095), Pin 6 ADC (3.3v scale from 0 to 4095), Pin 5 digital, Pin 6 digital
                I2C ------------------------ the I2C bytes read
                NXT_COLOR_FULL ------------- detected color, red light reflected, green lightreflected, blue light reflected, ambient light
                EV3_GYRO_ABS_DPS ----------- absolute rotation position in degrees, rotation rate in degrees per second
                EV3_COLOR_RAW_REFLECTED ---- red reflected light, unknown value (maybe a raw ambient value?)
                EV3_COLOR_COLOR_COMPONENTS - red reflected light, green reflected light, blue reflected light, unknown value (maybe a raw value?)
                EV3_INFRARED_SEEK ---------- a list for each of the four channels. For each channel heading (-25 to 25), distance (-128 or 0 to 100)
                EV3_INFRARED_REMOTE -------- a list for each of the four channels. For each channel red up, red down, blue up, blue down, boadcast
                
        """
        if self.SensorType[port] == self.SENSOR_TYPE.CUSTOM:
            #value, error = self.spi_read_32((self.BPSPI_MESSAGE_TYPE.READ_SENSOR + port))
            #value = int(value)
            #return [(value & 0x0FFF), ((value >> 12) & 0x0FFF), ((value >> 24) & 0x01), ((value >> 25) & 0x01)], error
            outArray = [self.SPI_Address, (self.BPSPI_MESSAGE_TYPE.READ_SENSOR + port), 0, 0, 0, 0, 0, 0, 0, 0]
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.SensorType[port] and reply[5] == self.SENSOR_STATE.VALID_DATA):
                    return [(((reply[8] & 0x0F) << 8) | reply[9]), (((reply[8] >> 4) & 0x0F) | (reply[7] << 4)), (reply[6] & 0x01), ((reply[6] >> 1) & 0x01)], self.SUCCESS
                else:
                    return [0 for b in range(4)], self.SENSOR_ERROR
            else:
                return [0 for b in range(4)], self.SPI_ERROR
        
        elif self.SensorType[port] == self.SENSOR_TYPE.I2C:
            outArray = [self.SPI_Address, (self.BPSPI_MESSAGE_TYPE.READ_SENSOR + port), 0, 0, 0, 0]
            for b in range(self.I2CInBytes[port]):
                outArray.append(0)
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.SensorType[port] and reply[5] == self.SENSOR_STATE.VALID_DATA and len(reply) - 6 == self.I2CInBytes[port]):
                    values = []
                    for b in range(6, len(reply)):
                        values.append(reply[b])
                    return values, self.SUCCESS
                else:
                    return [0 for b in range(self.I2CInBytes[port])], self.SENSOR_ERROR
            else:
                return [0 for b in range(self.I2CInBytes[port])], self.SPI_ERROR
        
        elif(self.SensorType[port] == self.SENSOR_TYPE.TOUCH
          or self.SensorType[port] == self.SENSOR_TYPE.NXT_TOUCH
          or self.SensorType[port] == self.SENSOR_TYPE.EV3_TOUCH
          or self.SensorType[port] == self.SENSOR_TYPE.NXT_ULTRASONIC
          or self.SensorType[port] == self.SENSOR_TYPE.EV3_COLOR_REFLECTED
          or self.SensorType[port] == self.SENSOR_TYPE.EV3_COLOR_AMBIENT
          or self.SensorType[port] == self.SENSOR_TYPE.EV3_COLOR_COLOR
          or self.SensorType[port] == self.SENSOR_TYPE.EV3_ULTRASONIC_LISTEN
          or self.SensorType[port] == self.SENSOR_TYPE.EV3_INFRARED_PROXIMITY):
            outArray = [self.SPI_Address, (self.BPSPI_MESSAGE_TYPE.READ_SENSOR + port), 0, 0, 0, 0, 0]
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if((reply[4] == self.SensorType[port] or (self.SensorType[port] == self.SENSOR_TYPE.TOUCH and (reply[4] == self.SENSOR_TYPE.NXT_TOUCH or reply[4] == self.SENSOR_TYPE.EV3_TOUCH))) and reply[5] == self.SENSOR_STATE.VALID_DATA):
                    return reply[6], self.SUCCESS
                else:
                    return 0, self.SENSOR_ERROR
            else:
                return 0, self.SPI_ERROR
        
        elif self.SensorType[port] == self.SENSOR_TYPE.NXT_COLOR_FULL:
            outArray = [self.SPI_Address, (self.BPSPI_MESSAGE_TYPE.READ_SENSOR + port), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.SensorType[port] and reply[5] == self.SENSOR_STATE.VALID_DATA):
                    return [reply[6], ((reply[7] << 2) | ((reply[11] >> 6) & 0x03)), ((reply[8] << 2) | ((reply[11] >> 4) & 0x03)), ((reply[9] << 2) | ((reply[11] >> 2) & 0x03)), ((reply[10] << 2) | (reply[11] & 0x03))], self.SUCCESS
                else:
                    return [0 for b in range(5)], self.SENSOR_ERROR
            else:
                return [0 for b in range(5)], self.SPI_ERROR
        
        elif(self.SensorType[port] == self.SENSOR_TYPE.NXT_LIGHT_ON
          or self.SensorType[port] == self.SENSOR_TYPE.NXT_LIGHT_OFF
          or self.SensorType[port] == self.SENSOR_TYPE.NXT_COLOR_RED
          or self.SensorType[port] == self.SENSOR_TYPE.NXT_COLOR_GREEN
          or self.SensorType[port] == self.SENSOR_TYPE.NXT_COLOR_BLUE
          or self.SensorType[port] == self.SENSOR_TYPE.NXT_COLOR_OFF
          or self.SensorType[port] == self.SENSOR_TYPE.EV3_GYRO_ABS
          or self.SensorType[port] == self.SENSOR_TYPE.EV3_GYRO_DPS
          or self.SensorType[port] == self.SENSOR_TYPE.EV3_ULTRASONIC_CM
          or self.SensorType[port] == self.SENSOR_TYPE.EV3_ULTRASONIC_INCHES):
            outArray = [self.SPI_Address, (self.BPSPI_MESSAGE_TYPE.READ_SENSOR + port), 0, 0, 0, 0, 0, 0]
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.SensorType[port] and reply[5] == self.SENSOR_STATE.VALID_DATA):
                    value = int((reply[6] << 8) | reply[7])
                    if((self.SensorType[port] == self.SENSOR_TYPE.EV3_GYRO_ABS
                    or self.SensorType[port] == self.SENSOR_TYPE.EV3_GYRO_DPS)
                    and (value & 0x1000)):
                        value = value - 0x10000
                    elif(self.SensorType[port] == self.SENSOR_TYPE.EV3_ULTRASONIC_CM
                      or self.SensorType[port] == self.SENSOR_TYPE.EV3_ULTRASONIC_INCHES):
                        value = value / 10
                    return value, self.SUCCESS
                else:
                    return 0, self.SENSOR_ERROR
            else:
                return 0, self.SPI_ERROR
        
        elif(self.SensorType[port] == self.SENSOR_TYPE.EV3_COLOR_RAW_REFLECTED
          or self.SensorType[port] == self.SENSOR_TYPE.EV3_GYRO_ABS_DPS):
            outArray = [self.SPI_Address, (self.BPSPI_MESSAGE_TYPE.READ_SENSOR + port), 0, 0, 0, 0, 0, 0, 0, 0]
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.SensorType[port] and reply[5] == self.SENSOR_STATE.VALID_DATA):
                    results = [int((reply[6] << 8) | reply[7]), int((reply[8] << 8) | reply[9])]
                    if self.SensorType[port] == self.SENSOR_TYPE.EV3_GYRO_ABS_DPS:
                        for r in range(len(results)):
                            if results[r] >= 0x8000:
                                results[r] = results[r] - 0x10000
                    return results, self.SUCCESS
                else:
                    return [0 for b in range(2)], self.SENSOR_ERROR
            else:
                return [0 for b in range(2)], self.SPI_ERROR
        
        elif(self.SensorType[port] == self.SENSOR_TYPE.EV3_COLOR_COLOR_COMPONENTS):
            outArray = [self.SPI_Address, (self.BPSPI_MESSAGE_TYPE.READ_SENSOR + port), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.SensorType[port] and reply[5] == self.SENSOR_STATE.VALID_DATA):
                    return [int((reply[6] << 8) | reply[7]), int((reply[8] << 8) | reply[9]), int((reply[10] << 8) | reply[11]), int((reply[12] << 8) | reply[13])], self.SUCCESS
                else:
                    return [0 for b in range(4)], self.SENSOR_ERROR
            else:
                return [0 for b in range(4)], self.SPI_ERROR
        
        elif(self.SensorType[port] == self.SENSOR_TYPE.EV3_INFRARED_SEEK):
            outArray = [self.SPI_Address, (self.BPSPI_MESSAGE_TYPE.READ_SENSOR + port), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.SensorType[port] and reply[5] == self.SENSOR_STATE.VALID_DATA):
                    results = [[int(reply[6]), int(reply[7])], [int(reply[8]), int(reply[9])], [int(reply[10]), int(reply[11])], [int(reply[12]), int(reply[13])]]
                    for c in range(len(results)):
                        for v in range(len(results[c])):
                            if results[c][v] > 0x80:
                                results[c][v] = results[c][v] - 0x100
                    return results, self.SUCCESS
                else:
                    return [[0 for b in range(2)] for v in range(4)], self.SENSOR_ERROR
            else:
                return [[0 for b in range(2)] for v in range(4)], self.SPI_ERROR
        
        elif(self.SensorType[port] == self.SENSOR_TYPE.EV3_INFRARED_REMOTE):
            outArray = [self.SPI_Address, (self.BPSPI_MESSAGE_TYPE.READ_SENSOR + port), 0, 0, 0, 0, 0, 0, 0, 0]
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.SensorType[port] and reply[5] == self.SENSOR_STATE.VALID_DATA):
                    results = [0, 0, 0, 0]
                    for r in range(len(results)):
                        value = int(reply[6 + r])
                        if value == 1:
                            results[r] = [1, 0, 0, 0, 0]
                        elif value == 2:
                            results[r] = [0, 1, 0, 0, 0]
                        elif value == 3:
                            results[r] = [0, 0, 1, 0, 0]
                        elif value == 4:
                            results[r] = [0, 0, 0, 1, 0]
                        elif value == 5:
                            results[r] = [1, 0, 1, 0, 0]
                        elif value == 6:
                            results[r] = [1, 0, 0, 1, 0]
                        elif value == 7:
                            results[r] = [0, 1, 1, 0, 0]
                        elif value == 8:
                            results[r] = [0, 1, 0, 1, 0]
                        elif value == 9:
                            results[r] = [0, 0, 0, 0, 1]
                        elif value == 10:
                            results[r] = [1, 1, 0, 0, 0]
                        elif value == 11:
                            results[r] = [0, 0, 1, 1, 0]
                        else:
                            results[r] = [0, 0, 0, 0, 0]
                    return results, self.SUCCESS
                else:
                    return [[0 for b in range(5)] for v in range(4)], self.SENSOR_ERROR
            else:
                return [[0 for b in range(5)] for v in range(4)], self.SPI_ERROR
        
        return 0, self.SENSOR_TYPE_ERROR #"Error, sensor not configured or not supported."#int(0) # not configured
    
    def set_motor_power(self, port, power):
        """
        Set the motor power in percent
        
        Keyword arguments:
        port -- The Motor port
        power -- The power from -100 to 100, or -128 for float
        """
        outArray = [self.SPI_Address, (self.BPSPI_MESSAGE_TYPE.WRITE_MOTOR_POWER + port), int(power)]
        self.spi_transfer_array(outArray)
    
    def set_motor_position(self, port, position):
        """
        Set the motor target position in degrees
        
        Keyword arguments:
        port -- The motor port
        position -- The target position
        """
        self.spi_write_32((self.BPSPI_MESSAGE_TYPE.WRITE_MOTOR_POSITION + port), int(position))
    
    def set_motor_dps(self, port, dps):
        """
        Set the motor target speed in degrees per second
        
        Keyword arguments:
        port -- The motor port
        dps -- The target speed in degrees per second
        """
        self.spi_write_16((self.BPSPI_MESSAGE_TYPE.WRITE_MOTOR_DPS + port), int(dps))
    
    def set_motor_limits(self, port, speed = 0, dps = 0):
        """
        Set the motor speed limit
        
        Keyword arguments:
        port -- The motor port
        speed -- The speed limit in percent (0 to 100) with 0 being no limit (100)
        dps -- The speed limit in degrees per second - Not yet supported in firmware!
        """
        dps = int(dps)
        outArray = [self.SPI_Address, (self.BPSPI_MESSAGE_TYPE.WRITE_MOTOR_LIMITS + port), int(speed), ((dps >> 8) & 0xFF), (dps & 0xFF)]
        print(outArray)
        self.spi_transfer_array(outArray)
    
    def get_motor_status(self, port):
        """
        Read a motor status
        
        Keyword arguments:
        port -- The motor port
        
        Returns a touple:
            list:
                flags -- 8-bits of bit-flags that indicate motor status:
                    bit 0 -- LOW_VOLTAGE_FLOAT - The motors are automatically disabled because the battery voltage is too low
                power -- the raw PWM power in percent (-100 to 100)
                encoder -- The encoder position
                dps -- The current speed in Degrees Per Second
            error
        """
        outArray = [self.SPI_Address, (self.BPSPI_MESSAGE_TYPE.READ_MOTOR_STATUS + port), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        reply = self.spi_transfer_array(outArray)
        if(reply[3] == 0xA5):
            speed = int(reply[5])
            if speed & 0x80:
                speed = speed - 0x100
            
            encoder = int((reply[6] << 24) | (reply[7] << 16) | (reply[8] << 8) | reply[9])
            if encoder & 0x80000000: # MT was 0x10000000, but I think it should be 0x80000000
                encoder = int(encoder - 0x100000000)
            
            dps = int((reply[10] << 8) | reply[11])
            if dps & 0x8000:
                dps = dps - 0x10000
            
            return [reply[4], speed, encoder, dps], self.SUCCESS
        return [0, 0, 0], self.SPI_ERROR
    
    def offset_motor_encoder(self, port, position):
        """
        Offset a motor encoder
        
        Keyword arguments:
        port -- The motor port
        offset -- The encoder offset
        
        Zero the encoder by offsetting it by the current position
        """
        self.spi_write_32((self.BPSPI_MESSAGE_TYPE.OFFSET_MOTOR_ENCODER + port), int(position))
    
    def get_motor_encoder(self, port):
        """
        Read a motor encoder in degrees
        
        Keyword arguments:
        port -- The motor port
        
        Returns the encoder position in degrees
        """
        encoder, error = self.spi_read_32(self.BPSPI_MESSAGE_TYPE.READ_MOTOR_ENCODER + port)
        if encoder & 0x80000000: # MT was 0x10000000, but I think it should be 0x80000000
            encoder = int(encoder - 0x100000000)
        #if encoder > 2147483647:
        #    encoder -= 4294967295
        return int(encoder), error
    
    def reset_all(self):
        """
        Reset the BrickPi. Set all the sensors' type to NONE, set the motors' speed to 0, and return control of the LED to the firmware.
        """
        # reset all sensors
        self.set_sensor_type(self.PORT_1, self.SENSOR_TYPE.NONE)
        self.set_sensor_type(self.PORT_2, self.SENSOR_TYPE.NONE)
        self.set_sensor_type(self.PORT_3, self.SENSOR_TYPE.NONE)
        self.set_sensor_type(self.PORT_4, self.SENSOR_TYPE.NONE)
        
        # turn off all motors
        self.set_motor_power(self.PORT_A, -128)
        self.set_motor_power(self.PORT_B, -128)
        self.set_motor_power(self.PORT_C, -128)
        self.set_motor_power(self.PORT_D, -128)
        
        # return the LED to the control of the FW
        self.set_led(-1)