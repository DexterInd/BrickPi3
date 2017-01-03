from __future__ import print_function
from __future__ import division
from builtins import input

import scratch
import re
import string
import math
import time
import sys

# Set to 1 to have debugging information printed out
# Set to 0 to go into quiet mode
en_debug = 1

import brickpi3
try:
    BP3 = brickpi3.BrickPi3()
    
    sensor_types = {
    'NONE'          : BP3.SENSOR_TYPE.NONE,
    'EV3US'         : BP3.SENSOR_TYPE.EV3_ULTRASONIC_CM,
    'EV3USCM'       : BP3.SENSOR_TYPE.EV3_ULTRASONIC_CM,
    'EV3USIN'       : BP3.SENSOR_TYPE.EV3_ULTRASONIC_INCHES,
    'EV3USLISTEN'   : BP3.SENSOR_TYPE.EV3_ULTRASONIC_LISTEN,
    'EV3GYRO'       : BP3.SENSOR_TYPE.EV3_GYRO_ABS,
    'EV3GYROABS'    : BP3.SENSOR_TYPE.EV3_GYRO_ABS,
    'EV3GYRODPS'    : BP3.SENSOR_TYPE.EV3_GYRO_DPS,
    'EV3GYROABSDPS' : BP3.SENSOR_TYPE.EV3_GYRO_ABS_DPS,
    'EV3IR'         : BP3.SENSOR_TYPE.EV3_INFRARED_PROXIMITY,
    'EV3IRPROX'     : BP3.SENSOR_TYPE.EV3_INFRARED_PROXIMITY,
    'EV3IRSEEK'     : BP3.SENSOR_TYPE.EV3_INFRARED_SEEK,
    'EV3IRREMOTE'   : BP3.SENSOR_TYPE.EV3_INFRARED_REMOTE,
    'EV3TOUCH'      : BP3.SENSOR_TYPE.EV3_TOUCH,
    'EV3COLOR'      : BP3.SENSOR_TYPE.EV3_COLOR_COLOR,
    'NXTUS'         : BP3.SENSOR_TYPE.NXT_ULTRASONIC,
    'ULTRASONIC'    : BP3.SENSOR_TYPE.NXT_ULTRASONIC,
    'NXTTOUCH'      : BP3.SENSOR_TYPE.NXT_TOUCH,
    'TOUCH'         : BP3.SENSOR_TYPE.TOUCH,
    'NXTCOLOR'      : BP3.SENSOR_TYPE.NXT_COLOR_FULL,
    'COLOR'         : BP3.SENSOR_TYPE.NXT_COLOR_FULL,
    'RAW'           : BP3.SENSOR_TYPE.CUSTOM,
    'TEMP'          : BP3.SENSOR_TYPE.CUSTOM,
    'FLEX'          : BP3.SENSOR_TYPE.CUSTOM 
    }
except IOError as error:
    print(error.args[0], ". Exiting...")
    sys.exit()

def get_regex_sensors():
    '''
    generate a regex ready string with all the sensor_types keys
    '''
    list_of_sensors = ""
    sorted_keys = sorted(sensor_types.keys(), key=len) # sort the keys by length
    for key in reversed(sorted_keys):                  # for each key ordered from longest to shortest
        if list_of_sensors != "":
            list_of_sensors +="|"
        list_of_sensors += key
    return list_of_sensors

def set_regex_string():
    '''
    Sets up the regex string, and the test_msgs for asserting

    regex explanation:
    1. (S[1-4]\s*({}): S1 to S4, potential spaces, one of the key in sensor_types
    2. S[1-4]\s*$:  S1 to S4, potential spaces, but no other characters
    3. M(?:OTOR)?\s*[A-D]\s*(ON|FULL|STOP|OFF|[0-9+]+\s*%?): 
            M or MOTOR, followed by A to D
            followed by keywords ON, FULL, STOP, OFF, or a value with or without a % sign
    4. UPDATE keyword
    '''
    regex_set_sensor = "S([1-4])\s*({})".format(get_regex_sensors())
    # group 1 -> sensor port
    # group 2 -> sensor type (as a string)

    regex_read_single_sensor = "S([1-4])\s*$"
    # group 3 -> sensor port

    # Nicole's regex
    # (?:M)(?:OTOR)?\s*([A-D])\s*(?:(ON|FULL|STOP|OFF|-?[0-9.]+\s*%?)|(?:(P)(?:osition|os)?\s*(-?[0-9.]+)))
    
    regex_set_motor = "(?:M)(?:OTOR)?\s*([A-D])\s*(P(?:osition|os)?)?\s*(ON|FULL|STOP|OFF|-?[0-9.]+)\s*%?"
    # group 4 -> motor port
    # group 5 -> motor speed

    regex_set_update_all = "(UPDATE)"
    # group 6 -> "UPDATE"

    return ("^"+regex_set_sensor+"|"+ \
                regex_read_single_sensor+"|"+ \
                regex_set_motor+"|"+  \
                regex_set_update_all)

compiled_regexBP = re.compile(set_regex_string(), re.IGNORECASE)


def is_BrickPi_msg(msg):
    '''
    Is the msg supposed to be handled by BrickPi3?
    Return: Boolean 
        True if valid for BrickPi3
        False otherwise
    '''
    retval = compiled_regexBP.match(msg.strip())
    
    if retval == None:
        return False
    else:
        return True

SensorType = ["NONE", "NONE", "NONE", "NONE"]

# temperature conversion lists for the dTemp sensor
_a = [0.003357042,         0.003354017,        0.0033530481,       0.0033536166]
_b = [0.00025214848,       0.00025617244,      0.00025420230,      0.000253772]
_c = [0.0000033743283,     0.0000021400943,    0.0000011431163,    0.00000085433271]
_d = [-0.000000064957311, -0.000000072405219, -0.000000069383563, -0.000000087912262]

def read_sensor(port):
    return_dict={}
    type = SensorType[port]
    value, error = BP3.get_sensor(port)
    
    if type != 'NONE':
        if error == BP3.SUCCESS:
            return_dict["S{} Status".format((port + 1))] = "SUCCESS"
        if error == BP3.SPI_ERROR:
            return_dict["S{} Status".format((port + 1))] = "SPI_ERROR"
        if error == BP3.SENSOR_ERROR:
            return_dict["S{} Status".format((port + 1))] = "SENSOR_ERROR"
        if error == BP3.SENSOR_TYPE_ERROR:
            return_dict["S{} Status".format((port + 1))] = "SENSOR_TYPE_ERROR"
    
    if type == 'EV3US' or type == 'EV3USCM':
        return_dict["S{} US cm".format((port + 1))] = value
    elif type == 'EV3USIN':
        return_dict["S{} US Inch".format((port + 1))] = value
    elif type == 'EV3USLISTEN':
        return_dict["S{} US Listen".format((port + 1))] = value
    elif type == 'EV3GYRO' or type == 'EV3GYROABS':
        return_dict["S{} Gyro ABS".format((port + 1))] = value
    elif type == 'EV3GYRODPS':
        return_dict["S{} Gyro DPS".format((port + 1))] = value
    elif type == 'EV3GYROABSDPS':
        return_dict["S{} Gyro ABS".format((port + 1))] = value[0]
        return_dict["S{} Gyro DPS".format((port + 1))] = value[1]
    elif type == 'EV3IR' or type == 'EV3IRPROX':
        return_dict["S{} IR Prox".format((port + 1))] = value
    elif type == 'EV3TOUCH' or type == 'NXTTOUCH' or type == 'TOUCH':
        return_dict["S{} Touch".format((port + 1))] = value
    elif type == 'EV3COLOR' or type == 'COLOR' or type == 'NXTCOLOR':
        return_dict["S{} Color".format((port + 1))] = value
    elif type == 'NXTUS' or type == 'ULTRASONIC':
        return_dict["S{} US cm".format((port + 1))] = value
    elif type == 'RAW':
        return_dict["S{} Raw".format((port + 1))] = value[0]
    elif type == 'TEMP':
        temp = 0
        if value[0] == 4095:
            return_dict["S{} Status".format((port + 1))] = "SENSOR_ERROR"
        elif error == BP3.SUCCESS:
            RtRt25 = (float)(value[0]) / (4095 - value[0])
            lnRtRt25 = math.log(RtRt25)
            if (RtRt25 > 3.277):
                i = 0
            elif (RtRt25 > 0.3599):
                i = 1
            elif (RtRt25 > 0.06816):
                i = 2
            else:
                i = 3
            temp =  1.0 / (_a[i] + (_b[i] * lnRtRt25) + (_c[i] * lnRtRt25 * lnRtRt25) + (_d[i] * lnRtRt25 * lnRtRt25 * lnRtRt25))
            temp = temp - 273.15
        return_dict["S{}".format((port + 1))] = temp
        return_dict["S{} Temp".format((port + 1))] = temp
    elif type == 'FLEX':
        return_dict["S{}".format((port + 1))] = value[0]
        return_dict["S{} Flex".format((port + 1))] = value[0]
    
    return return_dict

def handle_BrickPi_msg(msg):
    '''
    parses the message 
    returns a dictionary containing one or more sensor names 
        and corresponding values
    '''
    return_string ="0"
    return_dict={}
    
    if en_debug:
        print("received {}".format(msg.strip().lower()))
    
    regObj = compiled_regexBP.match(msg.strip().lower())
    if regObj == None:
        if en_debug:
            print ("BrickPi command is not recognized")
        return None

    #for i in regObj.groups():
    #    if en_debug:
    #        print (i)

    # the following are set to None when they are not required

    incoming_sensor_port = regObj.group(1)
    incoming_sensor_type = regObj.group(2)
    incoming_sensor_port_read = regObj.group(3)
    incoming_motor_port = regObj.group(4)
    incoming_motor_poscmd = regObj.group(5)
    incoming_motor_target = regObj.group(6)
    incoming_update_all = regObj.group(7)
    
    motor_name_to_number = {'A':0, 'B':1, 'C':2, 'D':3}
    motor_number_to_name = ['A', 'B', 'C', 'D']
    
    # READ A SPECIFIC SENSOR
    if incoming_sensor_port_read != None:
        # read that sensor value
        port = int(incoming_sensor_port_read) - 1 # convert the 1-4 to 0-3
        return_dict = read_sensor(port)
        
        if en_debug:
            print("Reading sensor port {}".format(incoming_sensor_port_read))

# hold off on this for now. for the EV3 IR sensor in remote mode: 4 strings (one per channel) with either "none" or else something like "red up, blu dw" 

    # SET SENSOR TYPE
    elif incoming_sensor_port != None and incoming_sensor_type != None:
        # set that port to that sensor
        port = int(incoming_sensor_port) - 1 # convert the 1-4 to 0-3
        sensor_type_string = incoming_sensor_type.upper()
        
        if (sensor_type_string == "RAW"
         or sensor_type_string == "TEMP"
         or sensor_type_string == "FLEX"):
            BP3.set_sensor_type(port, BP3.SENSOR_TYPE.CUSTOM, [(BP3.SENSOR_CUSTOM.PIN1_ADC)])
        else:
            BP3.set_sensor_type(port, sensor_types[sensor_type_string])
        SensorType[port] = sensor_type_string
        
        return_dict["S{} Type".format(incoming_sensor_port)] = sensor_type_string
        
        if en_debug:
            print("Setting sensor port {} to sensor {}".format(incoming_sensor_port, sensor_type_string))

    # SET MOTOR SPEED
    elif incoming_motor_port != None :
        port = motor_name_to_number[incoming_motor_port.upper()] # convert A-D to 0-3
        
        if incoming_motor_poscmd == None: # speed control
            if en_debug:
                print("Motor speed {}".format(incoming_motor_target))
            
            if incoming_motor_target == "on" or incoming_motor_target == "full":
                incoming_motor_target = 100
            elif incoming_motor_target == "off" or incoming_motor_target == "stop":
                incoming_motor_target = 0
            else:
                #try:
                #    incoming_motor_target = int(float(incoming_motor_target))
                incoming_motor_target = int(float(incoming_motor_target))
                #except TypeError:
                #    incoming_motor_target = "target error"
            
            if incoming_motor_target != "target error":
                BP3.set_motor_speed(port, incoming_motor_target)
            else:
                BP3.set_motor_speed(port, 0)  
        else:
            if en_debug:
                print("Motor position {}".format(incoming_motor_target))
            
            try:
                incoming_motor_target = int(float(incoming_motor_target))
            except TypeError:
                incoming_motor_target = "target error"
            
            if incoming_motor_target != "target error":
                BP3.set_motor_position(port, incoming_motor_target)
            else:
                BP3.set_motor_speed(port, 0)
        
        return_dict["Motor Target {}".format(incoming_motor_port.upper())] = incoming_motor_target
        
        
        if en_debug:
            print("setting motor {} to speed {}".format(incoming_motor_port, incoming_motor_target))

    # UPDATE ALL SENSOR VALUES
    elif incoming_update_all != None:
        for port in range(0, 4):
            return_dict.update(read_sensor(port))
            return_dict["Encoder {}".format(motor_number_to_name[port])] = BP3.get_motor_encoder(port)
        
        if en_debug:
            print("Update all sensor values")

    else:
        if en_debug:
            print("Unexpected error: {}".format(msg))
    
    if en_debug:
        print("Returning ", return_dict)
    
    return(return_dict)




if __name__ == '__main__':

    connected = 0   # This variable tells us if we're successfully connected.

    while(connected == 0):
        startTime = time.time()
        try:
            s = scratch.Scratch()
            if s.connected:
                if en_debug:
                    print("BrickPi Scratch: Connected to Scratch successfully")
            connected = 1   # We are succesfully connected!  Exit Away!
            # time.sleep(1)
        
        except scratch.ScratchError:
            arbitrary_delay = 10 # no need to issue error statement if at least 10 seconds haven't gone by.
            if (time.time() - startTime > arbitrary_delay):  
                print ("BrickPi Scratch: Scratch is either not opened or remote sensor connections aren't enabled")

    try:
        s.broadcast('READY')
    except NameError:
        if en_debug:
            print ("BrickPi Scratch: Unable to Broadcast")

    while True:
        try:
            m = s.receive()
            
            while m==None or m[0] == 'sensor-update' :
                m = s.receive()
            
            msg = m[1]
            
            if en_debug:
                print("Rx:{}".format(msg))
            sensors = handle_BrickPi_msg(msg)
            if sensors != None:
                s.sensorupdate(sensors)
                
        except KeyboardInterrupt:
            running= False
            if en_debug:
                print("BrickPi Scratch: Disconnected from Scratch")
            break
        except (scratch.scratch.ScratchConnectionError,NameError) as e:
            print("exception error: ", e)
            while True:
                #thread1.join(0)
                if en_debug:
                    print("BrickPi Scratch: Scratch connection error, Retrying")
                time.sleep(5)
                try:
                    s = scratch.Scratch()
                    s.broadcast('READY')
                    if en_debug:
                        print("BrickPi Scratch: Connected to Scratch successfully")
                    break;
                except scratch.ScratchError:
                    if en_debug:
                        print("BrickPi Scratch: Scratch is either not opened or remote sensor connections aren't enabled\n..............................\n")
        except:
            e = sys.exc_info()[0]
            if en_debug:
                print("BrickPi Scratch: Error %s" % e)
