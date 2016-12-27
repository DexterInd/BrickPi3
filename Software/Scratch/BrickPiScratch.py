from __future__ import print_function
from __future__ import division
from builtins import input

import scratch
import re
import string

import brickpi3 
import BrickPi 

# Set to 1 to have debugging information printed out
# Set to 0 to go into quiet mode
en_debug = 1

# set to 1 for regular use
# set to 0 in simulation mode, no brickpi3 attached.
try:
    BP3 = brickpi3.BrickPi3()
    en_brickpi3 = 1
    en_brickpi = 0
except:
    # TODO: add detection of BrickPi+ and first gen BrickPi
    en_brickpi3 = 0
    en_brickpi = 1


'''
This dictionary needs to be looked at
'''
if en_brickpi:
    sensor_types = {
    'EV3US' : TYPE_SENSOR_EV3_US_M0,        # Continuous measurement, distance, cm
    'EV3GYRO' : TYPE_SENSOR_EV3_GYRO_M0,            # Angle
    'EV3IR' : TYPE_SENSOR_EV3_INFRARED_M0,          # Proximity, 0 to 100
    'EV3TOUCH' : TYPE_SENSOR_EV3_TOUCH_DEBOUNCE,    # EV3 Touch sensor, debounced.
    'EV3COLOR' : TYPE_SENSOR_EV3_COLOR_M2,
    'ULTRASONIC' : TYPE_SENSOR_ULTRASONIC_CONT ,
    'TOUCH' : TYPE_SENSOR_TOUCH ,
    'COLOR' : TYPE_SENSOR_COLOR_FULL ,
    'RAW' : TYPE_SENSOR_RAW,
    'TEMP' : TYPE_SENSOR_RAW,
    'FLEX' : TYPE_SENSOR_RAW 
    }

if en_brickpi3:
    sensor_types = {
    #TODO fill in the proper dictionary for BrickPi3
    }


def get_regex_sensors():
    '''
    generate a regex ready string with all the sensor_types keys
    '''
    list_of_sensors = ""
    for key in sensor_types.keys():
        if list_of_sensors != "":
            list_of_sensors +="|"
        list_of_sensors += key
    return list_of_sensors

# test_msgs is used to assert the regex messages
test_msgs = []
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
    global test_msgs

    regex_set_sensor = "S([1-4])\s*({})".format(get_regex_sensors())
    # group 1 -> sensor port
    # group 2 -> sensor type (as a string)
    if en_brickpi:
        test_msgs += ["S1 EV3US",
            "S2EV3TOUCH",
            "S3  ULTRASONIC",
            "S4 TEMP "]

    # TODO: Adjust for BrickPi3
    if en_brickpi3:
        test_msgs += ["S1 EV3US",
            "S2EV3TOUCH",
            "S3  ULTRASONIC",
            "S4 TEMP "]

    regex_read_single_sensor = "S([1-4])\s*$"
    # group 3 -> sensor port
    test_msgs += ["S1",
        "S2",
        "S3",
        "S4"]

    regex_set_motor = "(?:M)(?:OTOR)?\s*([A-D])\s*(ON|FULL|STOP|OFF|-?[0-9.]+)\s*%?"
    # group 4 -> motor port
    # group 5 -> motor speed
    test_msgs += [
        "MAON",
        "MA FULL",
        "MOTOR A -50",
        "MB STOP",
        "MOTORBOFF",
        "MOTOR C 50",
        "MC50.5",
        "MOTOR D 100%",
        "MOTOR D 100 %",
        "MD-100"]

    regex_set_update_all = "(UPDATE)"
    # group 6 -> "UPDATE"
    test_msgs += ["Update"]

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

def handle_BrickPi_msg(msg):
    '''
    parses the message 
    returns a dictionary containing one or more sensor names 
        and corresponding values
    '''
    return_string ="0"
    return_dict={}

    print("received {}".format(msg.strip().lower()))
    
    regObj = compiled_regexBP.match(msg.strip().lower())
    if regObj == None:
        print ("BrickPi command is not recognized")
        return None

    # for i in regObj.groups():
    #     print (i)

    # the following are set to None when they are not required

    incoming_sensor_port = regObj.group(1)
    incoming_sensor_type = regObj.group(2)
    incoming_sensor_port_read = regObj.group(3)
    incoming_motor_port = regObj.group(4)
    incoming_motor_speed = regObj.group(5)
    incoming_update_all = regObj.group(6)


    # READ A SPECIFIC SENSOR
    if incoming_sensor_port_read != None:
        # read that sensor value
        if en_debug:
            print ("Reading sensor port {}".format(incoming_sensor_port_read))

    # SET SENSOR TYPE
    elif incoming_sensor_port != None and incoming_sensor_type != None:
        # set that port to that sensor
        if en_debug:
            print("Setting sensor port {} to sensor {}".format(
                        incoming_sensor_port, 
                        incoming_sensor_type))

    # SET MOTOR SPEED
    elif incoming_motor_port != None :
        print ("Got speed {}".format(incoming_motor_speed))
        if incoming_motor_speed == "on" or incoming_motor_speed == "full":
            incoming_motor_speed = 100
        elif incoming_motor_speed == "off" or incoming_motor_speed == "stop":
            incoming_motor_speed = 0
        else:
            incoming_motor_speed = int(float(incoming_motor_speed))

        if en_debug:
            print("setting motor {} to speed {}".format(incoming_motor_port,incoming_motor_speed))

        return_dict["Motor {}".format(incoming_motor_port.upper())] = incoming_motor_speed
        print (return_dict)

    # UPDATE ALL SENSOR VALUES
    elif incoming_update_all != None:
        if en_debug:
            print("Update all sensor values")

    else:
        print("Unexpected error: {}".format(msg))

    return(return_dict)




if __name__ == '__main__':

    for test_str in test_msgs:
        assert(is_BrickPi_msg(test_str))

    connected = 0   # This variable tells us if we're successfully connected.

    while(connected == 0):
        startTime = time.time()
        try:
            s = scratch.Scratch()
            if s.connected:
                print ("BrickPi Scratch: Connected to Scratch successfully")
            connected = 1   # We are succesfully connected!  Exit Away!
            # time.sleep(1)
        
        except scratch.ScratchError:
            arbitrary_delay = 10 # no need to issue error statement if at least 10 seconds haven't gone by.
            if (time.time() - startTime > arbitrary_delay):  
                print ("BrickPi Scratch: Scratch is either not opened or remote sensor connections aren't enabled")

    try:
        s.broadcast('READY')
    except NameError:
        print ("BrickPi Scratch: Unable to Broadcast")

    while True:
        try:
            m = s.receive()
            
            while m==None or m[0] == 'sensor-update' :
                m = s.receive()
            
            msg = m[1]

            print("Rx:{}".format(msg))
            sensors = handle_BrickPi_msg(msg)
            if sensors != None:
                s.sensorupdate(sensors)
                s.sensorupdate(sensors)
                
        except KeyboardInterrupt:
            running= False
            print ("BrickPi Scratch: Disconnected from Scratch")
            break
        except (scratch.scratch.ScratchConnectionError,NameError) as e:
            while True:
                #thread1.join(0)
                print ("BrickPi Scratch: Scratch connection error, Retrying")
                time.sleep(5)
                try:
                    s = scratch.Scratch()
                    s.broadcast('READY')
                    print ("BrickPi Scratch: Connected to Scratch successfully")
                    break;
                except scratch.ScratchError:
                    print ("BrickPi Scratch: Scratch is either not opened or remote sensor connections aren't enabled\n..............................\n")
        except:
            e = sys.exc_info()[0]
            print ("BrickPi Scratch: Error %s" % e  )

   


