# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2017 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# Python drivers for the BrickPi3

from __future__ import print_function
from __future__ import division
#from builtins import input

import subprocess # for executing system calls
import spidev
import array      # for converting hex string to byte array

FIRMWARE_VERSION_REQUIRED = "1.4.x" # Make sure the top 2 of 3 numbers match

BP_SPI = spidev.SpiDev()
BP_SPI.open(0, 1)
BP_SPI.max_speed_hz = 500000
BP_SPI.mode = 0b00
BP_SPI.bits_per_word = 8


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


class SensorError(Exception):
    """Exception raised if a sensor is not yet configured when trying to read it with get_sensor"""


def set_address(address, id):
    """
    Set the SPI address of the BrickPi3

    Keyword arguments:
    address -- the new SPI address to use (1 to 255)
    id -- the BrickPi3's unique serial number ID (so that the address can be set while multiple BrickPi3s are stacked on a Raspberry Pi).
    """
    address = int(address)
    if address < 1 or address > 255:
        raise IOError("brickpi3.set_address error: SPI address must be in the range of 1 to 255")
        return

    if(len(id) != 32):
        if id == "":
            id_arr = [0 for i in range(16)]
        else:
            raise IOError("brickpi3.set_address error: wrong serial number id length. Must be a 32-digit hex string.")
            return
    else:
        id_arr = array.array('B', bytearray.fromhex(id))
        if(len(id_arr) != 16):
            raise IOError("brickpi3.set_address error: unknown serial number id problem. Make sure to use a valid 32-digit hex string serial number.")
            return

    outArray = [0, BrickPi3.BPSPI_MESSAGE_TYPE.SET_ADDRESS, address]
    outArray.extend(id_arr)
    BP_SPI.xfer2(outArray)


class BrickPi3(object):
    PORT_1 = 0x01
    PORT_2 = 0x02
    PORT_3 = 0x04
    PORT_4 = 0x08

    PORT_A = 0x01
    PORT_B = 0x02
    PORT_C = 0x04
    PORT_D = 0x08

    MOTOR_FLOAT = -128

    SensorType = [0, 0, 0, 0]
    I2CInBytes = [0, 0, 0, 0]

    I2C_LENGTH_LIMIT = 16

    BPSPI_MESSAGE_TYPE = Enumeration("""
        NONE,

        GET_MANUFACTURER,
        GET_NAME,
        GET_HARDWARE_VERSION,
        GET_FIRMWARE_VERSION,
        GET_ID,
        SET_LED,
        GET_VOLTAGE_3V3,
        GET_VOLTAGE_5V,
        GET_VOLTAGE_9V,
        GET_VOLTAGE_VCC,
        SET_ADDRESS,

        SET_SENSOR_TYPE,

        GET_SENSOR_1,
        GET_SENSOR_2,
        GET_SENSOR_3,
        GET_SENSOR_4,

        I2C_TRANSACT_1,
        I2C_TRANSACT_2,
        I2C_TRANSACT_3,
        I2C_TRANSACT_4,

        SET_MOTOR_POWER,

        SET_MOTOR_POSITION,

        SET_MOTOR_POSITION_KP,

        SET_MOTOR_POSITION_KD,

        SET_MOTOR_DPS,

        SET_MOTOR_DPS_KP,

        SET_MOTOR_DPS_KD,

        SET_MOTOR_LIMITS,

        OFFSET_MOTOR_ENCODER,

        GET_MOTOR_A_ENCODER,
        GET_MOTOR_B_ENCODER,
        GET_MOTOR_C_ENCODER,
        GET_MOTOR_D_ENCODER,

        GET_MOTOR_A_STATUS,
        GET_MOTOR_B_STATUS,
        GET_MOTOR_C_STATUS,
        GET_MOTOR_D_STATUS,
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
        I2C_ERROR,
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
    """
    Flags for use with SENSOR_TYPE.CUSTOM

    PIN1_9V
        Enable 9V out on pin 1 (for LEGO NXT Ultrasonic sensor).

    PIN5_OUT
        Set pin 5 state to output. Pin 5 will be set to input if this flag is not set.

    PIN5_STATE
        If PIN5_OUT is set, this will set the state to output high, otherwise the state will
        be output low. If PIN5_OUT is not set, this flag has no effect.

    PIN6_OUT
        Set pin 6 state to output. Pin 6 will be set to input if this flag is not set.

    PIN6_STATE
        If PIN6_OUT is set, this will set the state to output high, otherwise the state will
        be output low. If PIN6_OUT is not set, this flag has no effect.

    PIN1_ADC
        Enable the analog/digital converter on pin 1 (e.g. for NXT analog sensors).

    PIN6_ADC
        Enable the analog/digital converter on pin 6.
    """

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
        OVERLOADED,
    """)

    MOTOR_STATUS_FLAG.LOW_VOLTAGE_FLOAT = 0x01 # If the motors are floating due to low battery voltage
    MOTOR_STATUS_FLAG.OVERLOADED        = 0x02 # If the motors aren't close to the target (applies to position control and dps speed control).

    #SUCCESS = 0
    #SPI_ERROR = 1
    #SENSOR_ERROR = 2
    #SENSOR_TYPE_ERROR = 3

    def __init__(self, addr = 1, detect = True): # Configure for the BrickPi. Optionally set the address (default to 1). Optionally disable detection (default to detect).
        """
        Do any necessary configuration, and optionally detect the BrickPi3

        Optionally specify the SPI address as something other than 1
        Optionally disable the detection of the BrickPi3 hardware. This can be used for debugging and testing when the BrickPi3 would otherwise not pass the detection tests.
        """

        if addr < 1 or addr > 255:
            raise IOError("error: SPI address must be in the range of 1 to 255")
            return

        self.SPI_Address = addr
        if detect == True:
            try:
                manufacturer = self.get_manufacturer()
                board = self.get_board()
                vfw = self.get_version_firmware()
            except IOError():
                raise IOError("No SPI response")
            if manufacturer != "Dexter Industries" or board != "BrickPi3":
                raise IOError("No SPI response")
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

        Returns:
        value
        """
        outArray = [self.SPI_Address, MessageType, 0, 0, 0, 0]
        reply = self.spi_transfer_array(outArray)
        if(reply[3] == 0xA5):
            return int((reply[4] << 8) | reply[5])
        raise IOError("No SPI response")
        return

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

        Returns :
        value
        """
        outArray = [self.SPI_Address, MessageType, 0, 0, 0, 0, 0, 0]
        reply = self.spi_transfer_array(outArray)
        if(reply[3] == 0xA5):
            return int((reply[4] << 24) | (reply[5] << 16) | (reply[6] << 8) | reply[7])
        raise IOError("No SPI response")
        return

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

        Returns:
        BrickPi3 manufacturer name string
        """
        outArray = [self.SPI_Address, self.BPSPI_MESSAGE_TYPE.GET_MANUFACTURER, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        reply = self.spi_transfer_array(outArray)
        if(reply[3] == 0xA5):
            name = ""
            for c in range(4, 24):
                if reply[c] != 0:
                    name += chr(reply[c])
                else:
                    break
            return name
        raise IOError("No SPI response")
        return

    def get_board(self):
        """
        Read the 20 charactor BrickPi3 board name

        Returns:
        BrickPi3 board name string
        """
        outArray = [self.SPI_Address, self.BPSPI_MESSAGE_TYPE.GET_NAME, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        reply = self.spi_transfer_array(outArray)
        if(reply[3] == 0xA5):
            name = ""
            for c in range(4, 24):
                if reply[c] != 0:
                    name += chr(reply[c])
                else:
                    break
            return name
        raise IOError("No SPI response")
        return

    def get_version_hardware(self):
        """
        Read the hardware version

        Returns:
        hardware version
        """
        version = self.spi_read_32(self.BPSPI_MESSAGE_TYPE.GET_HARDWARE_VERSION)
        return ("%d.%d.%d" % ((version / 1000000), ((version / 1000) % 1000), (version % 1000)))

    def get_version_firmware(self):
        """
        Read the firmware version

        Returns:
        firmware version
        """
        version = self.spi_read_32(self.BPSPI_MESSAGE_TYPE.GET_FIRMWARE_VERSION)
        return ("%d.%d.%d" % ((version / 1000000), ((version / 1000) % 1000), (version % 1000)))

    def get_id(self):
        """
        Read the 128-bit BrickPi hardware serial number

        Returns:
        serial number as 32 char HEX formatted string
        """
        outArray = [self.SPI_Address, self.BPSPI_MESSAGE_TYPE.GET_ID, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        reply = self.spi_transfer_array(outArray)
        if(reply[3] == 0xA5):
            return ("%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X" % (reply[4], reply[5], reply[6], reply[7], reply[8], reply[9], reply[10], reply[11], reply[12], reply[13], reply[14], reply[15], reply[16], reply[17], reply[18], reply[19]))
        raise IOError("No SPI response")
        return

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

        Returns:
        3.3v circuit voltage
        """
        value = self.spi_read_16(self.BPSPI_MESSAGE_TYPE.GET_VOLTAGE_3V3)
        return (value / 1000.0)

    def get_voltage_5v(self):
        """
        Get the 5v circuit voltage

        Returns:
        5v circuit voltage
        """
        value = self.spi_read_16(self.BPSPI_MESSAGE_TYPE.GET_VOLTAGE_5V)
        return (value / 1000.0)

    def get_voltage_9v(self):
        """
        Get the 9v circuit voltage

        Returns:
        9v circuit voltage
        """
        value = self.spi_read_16(self.BPSPI_MESSAGE_TYPE.GET_VOLTAGE_9V)
        return (value / 1000.0)

    def get_voltage_battery(self):
        """
        Get the battery voltage

        Returns:
        battery voltage
        """
        value = self.spi_read_16(self.BPSPI_MESSAGE_TYPE.GET_VOLTAGE_VCC)
        return (value / 1000.0)

    def set_sensor_type(self, port, type, params = 0):
        """
        Set the sensor type

        Keyword arguments:
        port -- The sensor port(s). PORT_1, PORT_2, PORT_3, and/or PORT_4.
        type -- The sensor type
        params = 0 -- the parameters needed for some sensor types.

        params is used for the following sensor types:
            CUSTOM -- a 16-bit integer used to configure the hardware.
            I2C -- a list of settings:
                params[0] -- Settings/flags
                params[1] -- target Speed in microseconds (0-255). Realistically the speed will vary.
                if SENSOR_I2C_SETTINGS_SAME flag set in I2C Settings:
                    params[2] -- Delay in microseconds between transactions.
                    params[3] -- Address
                    params[4] -- List of bytes to write
                    params[5] -- Number of bytes to read
        """
        for p in range(4):
            if port & (1 << p):
                self.SensorType[p] = type
        if(type == self.SENSOR_TYPE.CUSTOM):
            outArray = [self.SPI_Address, self.BPSPI_MESSAGE_TYPE.SET_SENSOR_TYPE, int(port), type, ((params[0] >> 8) & 0xFF), (params[0] & 0xFF)]

            #self.spi_write_24(self.BPSPI_MESSAGE_TYPE.SET_SENSOR_TYPE, int(port), ((type << 16) + (params[0])))
        elif(type == self.SENSOR_TYPE.I2C):
            if len(params) >= 2:
                outArray = [self.SPI_Address, self.BPSPI_MESSAGE_TYPE.SET_SENSOR_TYPE, int(port), type, params[0], params[1]] # Settings, SpeedUS
                if params[0] & self.SENSOR_I2C_SETTINGS.SAME and len(params) >= 6:
                    outArray.append((params[2] >> 24) & 0xFF) # DelayUS
                    outArray.append((params[2] >> 16) & 0xFF) #   ''
                    outArray.append((params[2] >> 8) & 0xFF)  #   ''
                    outArray.append(params[2] & 0xFF)         #   ''
                    outArray.append(params[3] & 0xFF)   # Address
                    outArray.append(params[5] & 0xFF)   # InBytes
                    for p in range(4):
                        if port & (1 << p):
                            self.I2CInBytes[p] = params[5] & 0xFF
                    outArray.append(len(params[4]))     # OutBytes
                    outArray.extend(params[4])          # OutArray
        else:
            outArray = [self.SPI_Address, self.BPSPI_MESSAGE_TYPE.SET_SENSOR_TYPE, int(port), type]

        self.spi_transfer_array(outArray)

    def transact_i2c(self, port, Address, OutArray, InBytes):
        """
        Conduct an I2C transaction

        Keyword arguments:
        port -- The sensor port (one at a time). PORT_1, PORT_2, PORT_3, or PORT_4.
        Address -- The I2C address for the device. Bits 1-7, not 0-6.
        OutArray -- A list of bytes to write to the device
        InBytes -- The number of bytes to read from the device
        """
        if port == self.PORT_1:
            message_type = self.BPSPI_MESSAGE_TYPE.I2C_TRANSACT_1
            port_index = 0
        elif port == self.PORT_2:
            message_type = self.BPSPI_MESSAGE_TYPE.I2C_TRANSACT_2
            port_index = 1
        elif port == self.PORT_3:
            message_type = self.BPSPI_MESSAGE_TYPE.I2C_TRANSACT_3
            port_index = 2
        elif port == self.PORT_4:
            message_type = self.BPSPI_MESSAGE_TYPE.I2C_TRANSACT_4
            port_index = 3
        else:
            raise IOError("transact_i2c error. Must be one sensor port at a time. PORT_1, PORT_2, PORT_3, or PORT_4.")
            return

        if self.SensorType[port_index] != self.SENSOR_TYPE.I2C:
            return
        outArray = [self.SPI_Address, message_type, Address, InBytes]
        self.I2CInBytes[port_index] = InBytes
        OutBytes = len(OutArray)
        if(OutBytes > self.I2C_LENGTH_LIMIT):
            outArray.append(self.I2C_LENGTH_LIMIT)
            for b in range(self.I2C_LENGTH_LIMIT):
                outArray.append(OutArray[b])
        else:
            outArray.append(OutBytes)
            outArray.extend(OutArray)
        self.spi_transfer_array(outArray)

    def get_sensor(self, port):
        """
        Read a sensor value

        Keyword arguments:
        port -- The sensor port (one at a time). PORT_1, PORT_2, PORT_3, or PORT_4.

        Returns the value(s) for the specified sensor.
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
                NXT_COLOR_FULL ------------- detected color, red light reflected, green light reflected, blue light reflected, ambient light
                EV3_GYRO_ABS_DPS ----------- absolute rotation position in degrees, rotation rate in degrees per second
                EV3_COLOR_RAW_REFLECTED ---- red reflected light, unknown value (maybe a raw ambient value?)
                EV3_COLOR_COLOR_COMPONENTS - red reflected light, green reflected light, blue reflected light, unknown value (maybe a raw value?)
                EV3_INFRARED_SEEK ---------- a list for each of the four channels. For each channel heading (-25 to 25), distance (-128 or 0 to 100)
                EV3_INFRARED_REMOTE -------- a list for each of the four channels. For each channel red up, red down, blue up, blue down, boadcast

        """
        if port == self.PORT_1:
            message_type = self.BPSPI_MESSAGE_TYPE.GET_SENSOR_1
            port_index = 0
        elif port == self.PORT_2:
            message_type = self.BPSPI_MESSAGE_TYPE.GET_SENSOR_2
            port_index = 1
        elif port == self.PORT_3:
            message_type = self.BPSPI_MESSAGE_TYPE.GET_SENSOR_3
            port_index = 2
        elif port == self.PORT_4:
            message_type = self.BPSPI_MESSAGE_TYPE.GET_SENSOR_4
            port_index = 3
        else:
            raise IOError("get_sensor error. Must be one sensor port at a time. PORT_1, PORT_2, PORT_3, or PORT_4.")
            return

        if self.SensorType[port_index] == self.SENSOR_TYPE.CUSTOM:
            outArray = [self.SPI_Address, message_type, 0, 0, 0, 0, 0, 0, 0, 0]
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.SensorType[port_index] and reply[5] == self.SENSOR_STATE.VALID_DATA):
                    return [(((reply[8] & 0x0F) << 8) | reply[9]), (((reply[8] >> 4) & 0x0F) | (reply[7] << 4)), (reply[6] & 0x01), ((reply[6] >> 1) & 0x01)]
                else:
                    raise SensorError("get_sensor error: Invalid sensor data")
                    return
            else:
                raise IOError("get_sensor error: No SPI response")
                return

        elif self.SensorType[port_index] == self.SENSOR_TYPE.I2C:
            outArray = [self.SPI_Address, message_type, 0, 0, 0, 0]
            for b in range(self.I2CInBytes[port_index]):
                outArray.append(0)
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.SensorType[port_index] and reply[5] == self.SENSOR_STATE.VALID_DATA and len(reply) - 6 == self.I2CInBytes[port_index]):
                    values = []
                    for b in range(6, len(reply)):
                        values.append(reply[b])
                    return values
                else:
                    raise SensorError("get_sensor error: Invalid sensor data")
                    return
            else:
                raise IOError("get_sensor error: No SPI response")
                return

        elif(self.SensorType[port_index] == self.SENSOR_TYPE.TOUCH
          or self.SensorType[port_index] == self.SENSOR_TYPE.NXT_TOUCH
          or self.SensorType[port_index] == self.SENSOR_TYPE.EV3_TOUCH
          or self.SensorType[port_index] == self.SENSOR_TYPE.NXT_ULTRASONIC
          or self.SensorType[port_index] == self.SENSOR_TYPE.EV3_COLOR_REFLECTED
          or self.SensorType[port_index] == self.SENSOR_TYPE.EV3_COLOR_AMBIENT
          or self.SensorType[port_index] == self.SENSOR_TYPE.EV3_COLOR_COLOR
          or self.SensorType[port_index] == self.SENSOR_TYPE.EV3_ULTRASONIC_LISTEN
          or self.SensorType[port_index] == self.SENSOR_TYPE.EV3_INFRARED_PROXIMITY):
            outArray = [self.SPI_Address, message_type, 0, 0, 0, 0, 0]
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if((reply[4] == self.SensorType[port_index] or (self.SensorType[port_index] == self.SENSOR_TYPE.TOUCH and (reply[4] == self.SENSOR_TYPE.NXT_TOUCH or reply[4] == self.SENSOR_TYPE.EV3_TOUCH))) and reply[5] == self.SENSOR_STATE.VALID_DATA):
                    return reply[6]
                else:
                    raise SensorError("get_sensor error: Invalid sensor data")
                    return
            else:
                raise IOError("get_sensor error: No SPI response")
                return

        elif self.SensorType[port_index] == self.SENSOR_TYPE.NXT_COLOR_FULL:
            outArray = [self.SPI_Address, message_type, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.SensorType[port_index] and reply[5] == self.SENSOR_STATE.VALID_DATA):
                    return [reply[6], ((reply[7] << 2) | ((reply[11] >> 6) & 0x03)), ((reply[8] << 2) | ((reply[11] >> 4) & 0x03)), ((reply[9] << 2) | ((reply[11] >> 2) & 0x03)), ((reply[10] << 2) | (reply[11] & 0x03))]
                else:
                    raise SensorError("get_sensor error: Invalid sensor data")
                    return
            else:
                raise IOError("get_sensor error: No SPI response")
                return

        elif(self.SensorType[port_index] == self.SENSOR_TYPE.NXT_LIGHT_ON
          or self.SensorType[port_index] == self.SENSOR_TYPE.NXT_LIGHT_OFF
          or self.SensorType[port_index] == self.SENSOR_TYPE.NXT_COLOR_RED
          or self.SensorType[port_index] == self.SENSOR_TYPE.NXT_COLOR_GREEN
          or self.SensorType[port_index] == self.SENSOR_TYPE.NXT_COLOR_BLUE
          or self.SensorType[port_index] == self.SENSOR_TYPE.NXT_COLOR_OFF
          or self.SensorType[port_index] == self.SENSOR_TYPE.EV3_GYRO_ABS
          or self.SensorType[port_index] == self.SENSOR_TYPE.EV3_GYRO_DPS
          or self.SensorType[port_index] == self.SENSOR_TYPE.EV3_ULTRASONIC_CM
          or self.SensorType[port_index] == self.SENSOR_TYPE.EV3_ULTRASONIC_INCHES):
            outArray = [self.SPI_Address, message_type, 0, 0, 0, 0, 0, 0]
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.SensorType[port_index] and reply[5] == self.SENSOR_STATE.VALID_DATA):
                    value = int((reply[6] << 8) | reply[7])
                    if((self.SensorType[port_index] == self.SENSOR_TYPE.EV3_GYRO_ABS
                    or self.SensorType[port_index] == self.SENSOR_TYPE.EV3_GYRO_DPS)
                    and (value & 0x8000)):
                        value = value - 0x10000
                    elif(self.SensorType[port_index] == self.SENSOR_TYPE.EV3_ULTRASONIC_CM
                      or self.SensorType[port_index] == self.SENSOR_TYPE.EV3_ULTRASONIC_INCHES):
                        value = value / 10
                    return value
                else:
                    raise SensorError("get_sensor error: Invalid sensor data")
                    return
            else:
                raise IOError("get_sensor error: No SPI response")
                return

        elif(self.SensorType[port_index] == self.SENSOR_TYPE.EV3_COLOR_RAW_REFLECTED
          or self.SensorType[port_index] == self.SENSOR_TYPE.EV3_GYRO_ABS_DPS):
            outArray = [self.SPI_Address, message_type, 0, 0, 0, 0, 0, 0, 0, 0]
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.SensorType[port_index] and reply[5] == self.SENSOR_STATE.VALID_DATA):
                    results = [int((reply[6] << 8) | reply[7]), int((reply[8] << 8) | reply[9])]
                    if self.SensorType[port_index] == self.SENSOR_TYPE.EV3_GYRO_ABS_DPS:
                        for r in range(len(results)):
                            if results[r] >= 0x8000:
                                results[r] = results[r] - 0x10000
                    return results
                else:
                    raise SensorError("get_sensor error: Invalid sensor data")
                    return
            else:
                raise IOError("get_sensor error: No SPI response")
                return

        elif(self.SensorType[port_index] == self.SENSOR_TYPE.EV3_COLOR_COLOR_COMPONENTS):
            outArray = [self.SPI_Address, message_type, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.SensorType[port_index] and reply[5] == self.SENSOR_STATE.VALID_DATA):
                    return [int((reply[6] << 8) | reply[7]), int((reply[8] << 8) | reply[9]), int((reply[10] << 8) | reply[11]), int((reply[12] << 8) | reply[13])]
                else:
                    raise SensorError("get_sensor error: Invalid sensor data")
                    return
            else:
                raise IOError("get_sensor error: No SPI response")
                return

        elif(self.SensorType[port_index] == self.SENSOR_TYPE.EV3_INFRARED_SEEK):
            outArray = [self.SPI_Address, message_type, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.SensorType[port_index] and reply[5] == self.SENSOR_STATE.VALID_DATA):
                    results = [[int(reply[6]), int(reply[7])], [int(reply[8]), int(reply[9])], [int(reply[10]), int(reply[11])], [int(reply[12]), int(reply[13])]]
                    for c in range(len(results)):
                        for v in range(len(results[c])):
                            if results[c][v] >= 0x80:
                                results[c][v] = results[c][v] - 0x100
                    return results
                else:
                    raise SensorError("get_sensor error: Invalid sensor data")
                    return
            else:
                raise IOError("get_sensor error: No SPI response")
                return

        elif(self.SensorType[port_index] == self.SENSOR_TYPE.EV3_INFRARED_REMOTE):
            outArray = [self.SPI_Address, message_type, 0, 0, 0, 0, 0, 0, 0, 0]
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.SensorType[port_index] and reply[5] == self.SENSOR_STATE.VALID_DATA):
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
                    return results
                else:
                    raise SensorError("get_sensor error: Invalid sensor data")
                    return
            else:
                raise IOError("get_sensor error: No SPI response")
                return

        raise IOError("get_sensor error: Sensor not configured or not supported.")
        return # sensor not configured or not supported.

    def set_motor_power(self, port, power):
        """
        Set the motor power in percent

        Keyword arguments:
        port -- The Motor port(s). PORT_A, PORT_B, PORT_C, and/or PORT_D.
        power -- The power from -100 to 100, or -128 for float
        """
        outArray = [self.SPI_Address, self.BPSPI_MESSAGE_TYPE.SET_MOTOR_POWER, int(port), int(power)]
        self.spi_transfer_array(outArray)

    def set_motor_position(self, port, position):
        """
        Set the motor target position in degrees

        Keyword arguments:
        port -- The motor port(s). PORT_A, PORT_B, PORT_C, and/or PORT_D.
        position -- The target position
        """
        position = int(position)
        outArray = [self.SPI_Address, self.BPSPI_MESSAGE_TYPE.SET_MOTOR_POSITION, int(port), ((position >> 24) & 0xFF), ((position >> 16) & 0xFF), ((position >> 8) & 0xFF), (position & 0xFF)]
        self.spi_transfer_array(outArray)

    def set_motor_position_relative(self, port, degrees):
        """
        Set the relative motor target position in degrees. Current position plus the specified degrees.

        Keyword arguments:
        port -- The motor port(s). PORT_A, PORT_B, PORT_C, and/or PORT_D.
        degrees -- The relative target position in degrees
        """
        for p in range(4):
            if port & (1 << p):
                self.set_motor_position((1 << p), (self.get_motor_encoder(1 << p) + degrees))

    def set_motor_position_kp(self, port, kp = 25):
        """
        Set the motor target position KP constant

        If you set kp higher, the motor will be more responsive to errors in position, at the cost of perhaps overshooting and oscillating.
        kd slows down the motor as it approaches the target, and helps to prevent overshoot.
        In general, if you increase kp, you should also increase kd to keep the motor from overshooting and oscillating.

        Keyword arguments:
        port -- The motor port(s). PORT_A, PORT_B, PORT_C, and/or PORT_D.
        kp -- The KP constant (default 25)
        """
        outArray = [self.SPI_Address, self.BPSPI_MESSAGE_TYPE.SET_MOTOR_POSITION_KP, int(port), int(kp)]
        self.spi_transfer_array(outArray)

    def set_motor_position_kd(self, port, kd = 70):
        """
        Set the motor target position KD constant

        If you set kp higher, the motor will be more responsive to errors in position, at the cost of perhaps overshooting and oscillating.
        kd slows down the motor as it approaches the target, and helps to prevent overshoot.
        In general, if you increase kp, you should also increase kd to keep the motor from overshooting and oscillating.

        Keyword arguments:
        port -- The motor port(s). PORT_A, PORT_B, PORT_C, and/or PORT_D.
        kd -- The KD constant (default 70)
        """
        outArray = [self.SPI_Address, self.BPSPI_MESSAGE_TYPE.SET_MOTOR_POSITION_KD, int(port), int(kd)]
        self.spi_transfer_array(outArray)

    def set_motor_dps(self, port, dps):
        """
        Set the motor target speed in degrees per second

        Keyword arguments:
        port -- The motor port(s). PORT_A, PORT_B, PORT_C, and/or PORT_D.
        dps -- The target speed in degrees per second
        """
        dps = int(dps)
        outArray = [self.SPI_Address, self.BPSPI_MESSAGE_TYPE.SET_MOTOR_DPS, int(port), ((dps >> 8) & 0xFF), (dps & 0xFF)]
        self.spi_transfer_array(outArray)

    def set_motor_limits(self, port, power = 0, dps = 0):
        """
        Set the motor speed limit

        Keyword arguments:
        port -- The motor port(s). PORT_A, PORT_B, PORT_C, and/or PORT_D.
        power -- The power limit in percent (0 to 100), with 0 being no limit (100)
        dps -- The speed limit in degrees per second, with 0 being no limit
        """
        dps = int(dps)
        outArray = [self.SPI_Address, self.BPSPI_MESSAGE_TYPE.SET_MOTOR_LIMITS, int(port), int(power), ((dps >> 8) & 0xFF), (dps & 0xFF)]
        self.spi_transfer_array(outArray)

    def get_motor_status(self, port):
        """
        Read a motor status

        Keyword arguments:
        port -- The motor port (one at a time). PORT_A, PORT_B, PORT_C, or PORT_D.

        Returns a list:
            flags -- 8-bits of bit-flags that indicate motor status:
                bit 0 -- LOW_VOLTAGE_FLOAT - The motors are automatically disabled because the battery voltage is too low
                bit 1 -- OVERLOADED - The motors aren't close to the target (applies to position control and dps speed control).
            power -- the raw PWM power in percent (-100 to 100)
            encoder -- The encoder position
            dps -- The current speed in Degrees Per Second
        """
        if port == self.PORT_A:
            message_type = self.BPSPI_MESSAGE_TYPE.GET_MOTOR_A_STATUS
        elif port == self.PORT_B:
            message_type = self.BPSPI_MESSAGE_TYPE.GET_MOTOR_B_STATUS
        elif port == self.PORT_C:
            message_type = self.BPSPI_MESSAGE_TYPE.GET_MOTOR_C_STATUS
        elif port == self.PORT_D:
            message_type = self.BPSPI_MESSAGE_TYPE.GET_MOTOR_D_STATUS
        else:
            raise IOError("get_motor_status error. Must be one motor port at a time. PORT_A, PORT_B, PORT_C, or PORT_D.")
            return

        outArray = [self.SPI_Address, message_type, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
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

            return [reply[4], speed, encoder, dps]
        raise IOError("No SPI response")
        return

    def get_motor_encoder(self, port):
        """
        Read a motor encoder in degrees

        Keyword arguments:
        port -- The motor port (one at a time). PORT_A, PORT_B, PORT_C, or PORT_D.

        Returns the encoder position in degrees
        """
        if port == self.PORT_A:
            message_type = self.BPSPI_MESSAGE_TYPE.GET_MOTOR_A_ENCODER
        elif port == self.PORT_B:
            message_type = self.BPSPI_MESSAGE_TYPE.GET_MOTOR_B_ENCODER
        elif port == self.PORT_C:
            message_type = self.BPSPI_MESSAGE_TYPE.GET_MOTOR_C_ENCODER
        elif port == self.PORT_D:
            message_type = self.BPSPI_MESSAGE_TYPE.GET_MOTOR_D_ENCODER
        else:
            raise IOError("get_motor_encoder error. Must be one motor port at a time. PORT_A, PORT_B, PORT_C, or PORT_D.")
            return

        encoder = self.spi_read_32(message_type)
        if encoder & 0x80000000:
            encoder = int(encoder - 0x100000000)
        return int(encoder)

    def offset_motor_encoder(self, port, position):
        """
        Offset a motor encoder

        Keyword arguments:
        port -- The motor port(s). PORT_A, PORT_B, PORT_C, and/or PORT_D.
        offset -- The encoder offset

        You can zero the encoder by offsetting it by the current position
        """
        position = int(position)
        outArray = [self.SPI_Address, self.BPSPI_MESSAGE_TYPE.OFFSET_MOTOR_ENCODER, int(port), ((position >> 24) & 0xFF), ((position >> 16) & 0xFF), ((position >> 8) & 0xFF), (position & 0xFF)]
        self.spi_transfer_array(outArray)

    def reset_motor_encoder(self, port):
        """
        Reset motor encoder(s) to 0

        Keyword arguments:
        port -- The motor port(s). PORT_A, PORT_B, PORT_C, and/or PORT_D.
        """
        if port & self.PORT_A:
            self.offset_motor_encoder(self.PORT_A, self.get_motor_encoder(self.PORT_A))

        if port & self.PORT_B:
            self.offset_motor_encoder(self.PORT_B, self.get_motor_encoder(self.PORT_B))

        if port & self.PORT_C:
            self.offset_motor_encoder(self.PORT_C, self.get_motor_encoder(self.PORT_C))

        if port & self.PORT_D:
            self.offset_motor_encoder(self.PORT_D, self.get_motor_encoder(self.PORT_D))

    def reset_all(self):
        """
        Reset the BrickPi. Set all the sensors' type to NONE, set the motors to float, and motors' limits and constants to default, and return control of the LED to the firmware.
        """
        # reset all sensors
        self.set_sensor_type(self.PORT_1 + self.PORT_2 + self.PORT_3 + self.PORT_4, self.SENSOR_TYPE.NONE)

        # turn off all motors
        self.set_motor_power(self.PORT_A + self.PORT_B + self.PORT_C + self.PORT_D, self.MOTOR_FLOAT)

        # reset motor limits
        self.set_motor_limits(self.PORT_A + self.PORT_B + self.PORT_C + self.PORT_D)

        # reset motor kP and kD constants
        self.set_motor_position_kp(self.PORT_A + self.PORT_B + self.PORT_C + self.PORT_D)
        self.set_motor_position_kd(self.PORT_A + self.PORT_B + self.PORT_C + self.PORT_D)

        # return the LED to the control of the FW
        self.set_led(-1)
