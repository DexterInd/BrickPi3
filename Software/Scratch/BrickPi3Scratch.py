import scratch
import re
import string
import math
import time
import sys
import brickpi3
import os # needed to create folders
try:
    sys.path.insert(0, os.path.join(os.path.expanduser("~"), 'Dexter/PivotPi/Software/Scratch/'))
    import PivotPiScratch
    pivotpi_available=True
except:
    pivotpi_available=False

try:
    sys.path.insert(0, os.path.join(os.path.expanduser("~"), 'Dexter/DI_Sensors/Scratch/'))
    import diSensorsScratch
    diSensorsScratch.detect_all()
    disensors_available=True
except:
    disensors_available=False

## Add what's required to have modal popup windows
## and handle crashes if any
from Tkinter import *
import tkMessageBox
import atexit

def error_box(in_string):
    '''
    Code to generate popup window
    '''
    window = Tk()
    window.wm_withdraw()

    #message at x:200,y:200
    window.geometry("1x1+"+str(window.winfo_screenwidth()//2)+"+"+str(window.winfo_screenheight()//2))
    tkMessageBox.showerror(title="error",message=in_string,parent=window)

@atexit.register
def cleanup():
    '''
    Stop BrickPi3 and print out error msg
    if I can figure out how to differentiate between normal exit and crash
    then I'll consider having a popup window here.
    '''
    try:
        BP3.reset_all() # we want the brickpi3 to stop if BrickPi3Scratch.py crashes
    except:
        pass
    print ("Scratch Interpreted closed")


##################################################################
# GLOBAL VARIABLES
##################################################################

# Set to 1 to have debugging information printed out
# Set to 0 to go into quiet mode
en_debug = 1
success_code = "SUCCESS"

try:
    BP3 = brickpi3.BrickPi3()
    bp3ports = [BP3.PORT_1, BP3.PORT_2, BP3.PORT_3, BP3.PORT_4]
    bp3motors = [BP3.PORT_A, BP3.PORT_B, BP3.PORT_C, BP3.PORT_D]

    sensor_types = {
    'NONE'          : [BP3.SENSOR_TYPE.NONE, "None"],
    'EV3US'         : [BP3.SENSOR_TYPE.EV3_ULTRASONIC_CM, "US cm"],
    'EV3USCM'       : [BP3.SENSOR_TYPE.EV3_ULTRASONIC_CM, "US cm"],
    'EV3USIN'       : [BP3.SENSOR_TYPE.EV3_ULTRASONIC_INCHES, "US Inch"],
    'EV3USLISTEN'   : [BP3.SENSOR_TYPE.EV3_ULTRASONIC_LISTEN, "US Listen"],
    'EV3GYRO'       : [BP3.SENSOR_TYPE.EV3_GYRO_ABS, "Gyro ABS"],
    'EV3GYROABS'    : [BP3.SENSOR_TYPE.EV3_GYRO_ABS, "Gyro ABS"],
    'EV3GYRODPS'    : [BP3.SENSOR_TYPE.EV3_GYRO_DPS, "Gyro DPS"],
    'EV3GYROABSDPS' : [BP3.SENSOR_TYPE.EV3_GYRO_ABS_DPS, "Gyro ABS", "Gyro DPS"],
    'EV3IR'         : [BP3.SENSOR_TYPE.EV3_INFRARED_PROXIMITY, "IR Prox"],
    'EV3IRPROX'     : [BP3.SENSOR_TYPE.EV3_INFRARED_PROXIMITY, "IR Prox"],
    'EV3IRSEEK'     : [BP3.SENSOR_TYPE.EV3_INFRARED_SEEK, "None"],
    'EV3IRREMOTE'   : [BP3.SENSOR_TYPE.EV3_INFRARED_REMOTE, "None"],
    'EV3TOUCH'      : [BP3.SENSOR_TYPE.EV3_TOUCH, "Touch"],
    'EV3COLOR'      : [BP3.SENSOR_TYPE.EV3_COLOR_COLOR, "Color"],
    'NXTUS'         : [BP3.SENSOR_TYPE.NXT_ULTRASONIC, "US cm"],
    'ULTRASONIC'    : [BP3.SENSOR_TYPE.NXT_ULTRASONIC, "US cm"],
    'NXTTOUCH'      : [BP3.SENSOR_TYPE.NXT_TOUCH, "Touch"],
    'TOUCH'         : [BP3.SENSOR_TYPE.TOUCH, "Touch"],
    'NXTCOLOR'      : [BP3.SENSOR_TYPE.NXT_COLOR_FULL, "Color"],
    'COLOR'         : [BP3.SENSOR_TYPE.NXT_COLOR_FULL, "Color"],
    'RAW'           : [BP3.SENSOR_TYPE.CUSTOM, "Raw"],
    'TEMP'          : [BP3.SENSOR_TYPE.CUSTOM, "Temp"],
    'FLEX'          : [BP3.SENSOR_TYPE.CUSTOM, "Flex"]
    }

## Handle Firmware Version Error with a popup instead of quietly dying
## and leaving the user wondering why their program isn't working
except brickpi3.FirmwareVersionError as error:
    error_box("BrickPi Robot needs to be updated (see DI Update Software)")
    print ("Scratch Interpreted closed: {}".format(error.args[0]))
    sys.exit()
except IOError as error:
    error_box("Connection Error: {}".format(error.args[0]))
    print(f"{error.args[0]}. Exiting...")
    sys.exit()
except:
    error_box("Unknown Error, closing Scratch Interpreter")

SensorType = ["NONE", "NONE", "NONE", "NONE"]
defaultCameraFolder = os.path.join(os.path.expanduser("~"), "Desktop/")
cameraFolder = defaultCameraFolder

# temperature conversion lists for the dTemp sensor
_a = [0.003357042,         0.003354017,        0.0033530481,       0.0033536166]
_b = [0.00025214848,       0.00025617244,      0.00025420230,      0.000253772]
_c = [0.0000033743283,     0.0000021400943,    0.0000011431163,    0.00000085433271]
_d = [-0.000000064957311, -0.000000072405219, -0.000000069383563, -0.000000087912262]


##################################################################
# HELPER FUNCTIONS
##################################################################

def get_regex_sensors():
    '''
    generate a regex ready string with all the sensor_types keys
    '''
    list_of_sensors = ""

    # sort the keys by length
    sorted_keys = sorted(sensor_types.keys(), key=len)

    # for each key ordered from longest to shortest
    for key in reversed(sorted_keys):
        if list_of_sensors != "":
            list_of_sensors += "|"
        list_of_sensors += key
    return list_of_sensors


def set_regex_string():
    '''
    Sets up the regex string, and the test_msgs for asserting

    regex explanation:
    1. (S[1-4]\s*({}):  S1 to S4, potential spaces,
                        one of the key in sensor_types
    2. S[1-4]\s*$:  S1 to S4, potential spaces, but no other characters
    3. M(?:OTOR)?\s*[A-D]\s*(ON|FULL|STOP|OFF|[0-9+]+\s*%?):
            M or MOTOR, followed by A to D
            followed by keywords ON, FULL, STOP, OFF,
            or a value with or without a % sign
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

    regex_set_update_all = "\s*(UPDATE)\s*"
    # group 6 -> "UPDATE"

    # Add a reset
    regex_reset = "\s*(RESET)\s*"

    # Read a motor speed
    reget_read_motor = "(?:M)(?:OTOR)?\s*([A-D])\s*"

    return ("^" + regex_set_sensor + "|" +
                regex_read_single_sensor + "|" +
                regex_set_motor + "|" +
                regex_set_update_all + "|" +
                regex_reset + "|" +
                reget_read_motor)


def is_BrickPi_msg(msg):
    '''
    Is the msg supposed to be handled by BrickPi3?
    Return: Boolean
        True if valid for BrickPi3
        False otherwise
    '''
    retval = compiled_regexBP.match(msg.strip())

    if retval is None:
        return False
    else:
        # print ("Recognized {}".format(msg))
        return True


def read_sensor(port_index):

    return_dict = {}
    bp3_port = bp3ports[port_index]

    type = SensorType[port_index]
    try:
        value = BP3.get_sensor(bp3_port)
        valid_reading = True
    except Exception as e:
        print ("failing to read_sensor: {}".format(e))
        valid_reading = False
        return_dict["S{} Status".format(port_index+1)] = e

    try:
        if valid_reading:
            # print ("got {} from {}".format(value,port_index))


            if type != 'TEMP':  # the temp sensor is a peculiar case
                try:
                    # this is for a sensor returning more than one value
                    # (ie value is a list object)
                    # some sensors return more than one value
                    # but we are only interested in the first one
                    # Raw and Flex are examples of this situation
                    # using zip will iterate over both lists
                    # allowing iteration over the shortest of the
                    # two lists
                    for out_str, out_value in zip(sensor_types[type][1:], value):
                        return_dict["S{} {}".format((port_index+1), out_str)] = out_value
                        return_dict["S{} Status".format(port_index+1)] = success_code

                # TypeError is generated if we attempt to iterate over
                # a non-iterable object
                # in other words, value was a number, not a list
                except TypeError:
                    # for a sensor returning just one value:
                    return_dict["S{} {}".format((port_index+1),sensor_types[type][1])] = value
                    return_dict["S{} Status".format(port_index+1)] = success_code

            elif type == 'TEMP':
                temp = 0
                if value[0] == 4095:
                    return_dict["S{} Status".format((port_index+1))] = "SENSOR_ERROR"
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
                    temp = 1.0 / (_a[i] + (_b[i] * lnRtRt25) + (_c[i] * lnRtRt25 * lnRtRt25) + (_d[i] * lnRtRt25 * lnRtRt25 * lnRtRt25))
                    temp = temp - 273.15

                return_dict["S{} {}".format((port_index + 1), sensor_types[type][1])] = temp
                return_dict["S{} Status".format(port_index+1)] = success_code
            else:
                # we really should never get here. Should we handle this case
                # or just let it pass?
                pass
    except Exception as e:
        print (e)


    return return_dict

def read_encoder_values(port_index, name):
    # unpack the tuple here as Scratch can't do it
    return_encoder = {}

    try:
        value = BP3.get_motor_encoder(bp3motors[port_index])
        return_encoder["Encoder {}".format(name)] = value
        return_encoder["Encoder {} Status".format(name)] = success_code
    except Exception as e:
        return_encoder["Encoder {} Status".format(name)] = e
        # print ("read_encoder_value: {}".format(e))

    return return_encoder


def BP_reset():
    '''
    Resets the BrickPi3
    '''

    global SensorType
    SensorType = ["NONE", "NONE", "NONE", "NONE"]

    for port in range(4):
        BP3.set_sensor_type(bp3ports[port], sensor_types["NONE"][0])


def handle_BrickPi_msg(msg):
    '''
    parses the message
    returns a dictionary containing one or more sensor names
        and corresponding values
    '''
    return_string = "0"
    return_dict = {}

    # if en_debug:
        # print("received {}".format(msg.strip().lower()))

    regObj = compiled_regexBP.match(msg.strip().lower())
    if regObj is None:
        if en_debug:
            print ("BrickPi3 command is not recognized")
        return None

    # the following are set to None when they are not required
    incoming_sensor_port = regObj.group(1)
    incoming_sensor_type = regObj.group(2)
    incoming_sensor_port_read = regObj.group(3)
    incoming_motor_port = regObj.group(4)
    incoming_motor_poscmd = regObj.group(5)
    incoming_motor_target = regObj.group(6)
    incoming_update_all = regObj.group(7)
    incoming_reset = regObj.group(8)
    incoming_motor_read = regObj.group(9)

    motor_name_to_number = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    motor_number_to_name = ['A', 'B', 'C', 'D']

    # READ A SPECIFIC SENSOR
    # valid when the broadcast msg is simply S1 to S4
    if incoming_sensor_port_read is not None:
        # read that sensor value
        port_index = int(incoming_sensor_port_read) - 1  # convert the 1-4 to 0-3
        return_dict = read_sensor(port_index)

        # if en_debug:
        #     print("Reading sensor port {}".format(incoming_sensor_port_read))

# hold off on this for now.
# for the EV3 IR sensor in remote mode:
#       4 strings (one per channel)
#       with either "none"
#       or else something like "red up, blu dw"

    # SET and READ SENSOR TYPE
    elif incoming_sensor_port is not None and incoming_sensor_type is not None:
        # set that port to that sensor
        port_index = int(incoming_sensor_port) - 1  # convert the 1-4 to 0-3
        bp3_portaddress = bp3ports[port_index]
        sensor_type_string = incoming_sensor_type.upper()

        if SensorType[port_index] != sensor_type_string:
            # print("Setting sensor type")
            if (sensor_type_string == "RAW"
             or sensor_type_string == "TEMP"
             or sensor_type_string == "FLEX"):
                BP3.set_sensor_type(bp3_portaddress, BP3.SENSOR_TYPE.CUSTOM, [(BP3.SENSOR_CUSTOM.PIN1_ADC)])
            else:
                BP3.set_sensor_type(bp3_portaddress,
                                    sensor_types[sensor_type_string][0])

            SensorType[port_index] = sensor_type_string

            # don't return sensor Type as it seems useless and just makes a busier sensor value list
            # return_dict["S{} Type".format(incoming_sensor_port)] = sensor_type_string
            if en_debug:
                print(f"Setting sensor port {incoming_sensor_port} to sensor {sensor_type_string}")
            time.sleep(0.010)

        return_dict.update(read_sensor(port_index))

        if en_debug:
            print(f"Reading sensor port {incoming_sensor_port}")

    # SET MOTOR SPEED
    elif incoming_motor_port is not None :

        # convert A-D to 0-3
        motor_index = motor_name_to_number[incoming_motor_port.upper()]


        if incoming_motor_poscmd is None: # speed control
            # if en_debug:
            #     print("Motor speed {}".format(incoming_motor_target))

            if incoming_motor_target == "on" or \
               incoming_motor_target == "full":
                incoming_motor_target = 100
            elif incoming_motor_target == "off" or incoming_motor_target == "stop":
                incoming_motor_target = 0
            else:
                # try:
                #    incoming_motor_target = int(float(incoming_motor_target))
                incoming_motor_target = int(float(incoming_motor_target))
                # except TypeError:
                #    incoming_motor_target = "target error"

            if incoming_motor_target != "target error":
                BP3.set_motor_power(bp3motors[motor_index], incoming_motor_target)
            else:
                BP3.set_motor_power(bp3motors[motor_index], 0)

        else:  # position control
            # if en_debug:
            #     print("Motor position {}".format(incoming_motor_target))

            try:
                incoming_motor_target = int(float(incoming_motor_target))
                BP3.set_motor_position(bp3motors[motor_index],
                                       incoming_motor_target)
                # print("Motor {} moved to {}".format(motor_index,incoming_motor_target))
            except TypeError:
                incoming_motor_target = "target error"
                BP3.set_motor_power(bp3motors[motor_index], 0)

        # returning Motor Target is meaningless as it's exactly what Scratch passed to us
        # return_dict["Motor Target {}".format(incoming_motor_port.upper())] = incoming_motor_target

        return_dict.update(read_encoder_values(motor_index,motor_number_to_name[motor_index]))

        # this is error inducing when setting motor to a specific position
        # if en_debug:
        #     print("setting motor {} to speed {}".format(incoming_motor_port, incoming_motor_target))

    # UPDATE ALL SENSOR VALUES
    elif incoming_update_all is not None:

        for port in range(0, 4):
            return_dict.update(read_sensor(port))
            return_dict.update(read_encoder_values(port,motor_number_to_name[port]))

        if en_debug:
            print("Update all sensor values")

    # ADD A RESET - NP 19 Jan 2017
    elif incoming_reset is not None:
        BP_reset()

    # Read a motor position
    elif incoming_motor_read is not None:
        motor_index = motor_name_to_number[incoming_motor_read.upper()]
        # print("incoming motor read: {}".format(incoming_motor_read))
        return_dict.update(read_encoder_values(motor_index,
                                      motor_number_to_name[motor_index]))

    else:
        if en_debug:
            print(f"Unexpected error: {msg}")

    # if en_debug:
    #     print("Returning ", return_dict)

    return(return_dict)


##################################################################
# MAIN FUNCTION
##################################################################
compiled_regexBP = re.compile(set_regex_string(), re.IGNORECASE)

if __name__ == '__main__':

    connected = 0   # This variable tells us if we're successfully connected.

    while(connected == 0):
        startTime = time.time()
        try:
            s = scratch.Scratch()
            if s.connected:
                if en_debug:
                    print("BrickPi3 Scratch: Connected to Scratch successfully")
            connected = 1   # We are succesfully connected!  Exit Away!
            # time.sleep(1)

        except scratch.ScratchError:
            arbitrary_delay = 10  # no need to issue error statement if at least 10 seconds haven't gone by.
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

            while m is None or m[0] == 'sensor-update' :

                # keep this for reference.
                # may work to detect File/new, File/Open but needs a change in scratchpi
                # to detect "send_vars" msg as being valid
                # if m[0] == "send_vars":  # File/New
                #     print("Resetting everything")
                #     SensorType = ["None","None","None","None"]
                #     for port in range(4):
                #         BP3.set_sensor_type(bp3ports[port], sensor_types["NONE"][0])

                m = s.receive()

            msg = m[1]

# remove all spaces in the input msg to create ms_nospace
# brickpi3 handles the one without spaces but we keep the one with spaces
# for others (like pivotpi, camera, line_sensor) as a precautionary measure.
            try:
                msg_nospace = msg.replace(" ","")
            except:
                pass


            if en_debug:
                print(f"Rx:{msg}")

            if is_BrickPi_msg(msg_nospace):
                sensors = handle_BrickPi_msg(msg_nospace)
                if sensors is not None:
                    s.sensorupdate(sensors)

            # CREATE FOLDER TO SAVE PHOTOS IN

            elif msg[:6].lower()=="FOLDER".lower():
                print ("Camera folder")
                try:
                    cameraFolder=defaultCameraFolder+str(msg[6:]).strip()
                    print(cameraFolder)
                    if not os.path.exists(cameraFolder):
                        pi=1000  # uid and gid of user pi
                        os.makedirs(cameraFolder)
                        os.chown(cameraFolder,pi,pi)
                        s.sensorupdate({"folder":"created"})
                    else:
                        s.sensorupdate({"folder":"set"})
                except:
                    print ("error with folder name")

            # TAKE A PICTURE

            elif msg.lower()=="TAKE_PICTURE".lower():
                print ("TAKE_PICTURE" )
                pi=1000  # uid and gid of user pi
                try:
                    from subprocess import call
                    import datetime
                    newimage = "{}/img_{}.jpg".format(cameraFolder,str(datetime.datetime.now()).replace(" ","_",10))
                    photo_cmd="raspistill -o {} -w 640 -h 480 -t 1".format(newimage)
                    call ([photo_cmd], shell=True)
                    os.chown(newimage,pi,pi)
                    if en_debug:
                        print ("Picture Taken")
                    s.sensorupdate({'camera':"Picture Taken"})
                except:
                    if en_debug:
                        e = sys.exc_info()[1]
                        print ("Error taking picture")
                    s.sensorupdate({'camera':"Error"})


            elif (msg[:5].lower()=="SPEAK".lower() or msg[:3].lower()=="SAY".lower() ):
                try:
                    from subprocess import call
                    cmd_beg = "espeak -ven+f1 "
                    if (msg[:5].lower() == "speak"):
                        in_text = msg[5:]
                    else:
                        in_text = msg[3:]
                    cmd_end = " 2>/dev/null"
                    out_str = cmd_beg+"\""+in_text+"\""+cmd_end
                    if en_debug:
                        print(out_str)
                    call([out_str], shell=True)

                except:
                    print("Issue with espeak")

            # PIVOTPI
            elif pivotpi_available==True and PivotPiScratch.isPivotPiMsg(msg):
                pivotsensors = PivotPiScratch.handlePivotPi(msg)
                # print "Back from PivotPi",pivotsensors
                s.sensorupdate(pivotsensors)

            # DI Sensors
            elif disensors_available==True and diSensorsScratch.isDiSensorsMsg(msg):
                disensors = diSensorsScratch.handleDiSensors(msg)
                s.sensorupdate(disensors)


            else:
                if en_debug:
                    print ("Ignoring Command: {}".format(msg))

        except KeyboardInterrupt:
            running = False
            if en_debug:
                print("BrickPi Scratch: Disconnected from Scratch")
            break
        except (scratch.scratch.ScratchConnectionError, NameError) as e:
            print(f"exception error: {e}")
            while True:
                # thread1.join(0)
                if en_debug:
                    print("BrickPi Scratch: Scratch connection error, Retrying")
                time.sleep(5)
                try:
                    s = scratch.Scratch()
                    s.broadcast('READY')
                    if en_debug:
                        print("BrickPi Scratch: Connected to Scratch successfully")
                    break
                except scratch.ScratchError:
                    if en_debug:
                        print("BrickPi Scratch: Scratch is either not opened or remote sensor connections aren't enabled\n..............................\n")
        except:
            e = sys.exc_info()[0]
            if en_debug:
                print(f"BrickPi Scratch: Error {e}")
