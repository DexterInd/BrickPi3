# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for reading a Dexter Industries pressure sensor connected to PORT_1 of the BrickPi3

from __future__ import print_function
from __future__ import division

import time
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3()

BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.CUSTOM, [(BP.SENSOR_CUSTOM.PIN1_ADC)]) # Configure for a Dexter Industries pressure sensor (analog on sensor port pin 1).

try:
    while True:
        value = BP.get_sensor(BP.PORT_1)[0][0] # read the sensor port value
        if(value < 4095):
            print("Pressure: %6.2fkPa" % (((value / 4095) - 0.04) / 0.0018)) # print the value for the dPressure 500
            #print("Pressure: %6.2fkPa" % (((value / 4095) - 0.04) / 0.00369)) # print the value for the dPressure 250
        else:
            print("Pressure: (disconnected)")
        time.sleep(0.02)         # delay 20ms
except KeyboardInterrupt:
    BP.reset_all()

#DPRESS_VREF = 4.85
#BrickPiSetup()  # setup the serial port for communication
#BrickPi.SensorType[PORT_3] = TYPE_SENSOR_RAW
#if not BrickPiSetupSensors() :
#    while True :
#        if not BrickPiUpdateValues() :
#            # Pressure is calculated using Vout = VS x (0.00369 x P + 0.04)
#            # Where Vs is assumed to be equal to around 4.85 on the NXT
#            # Get raw sensor value
#            val = BrickPi.Sensor[PORT_3]
#            # Calculate Vout
#            Vout = ((val * DPRESS_VREF) / 1023)
#            pressure = ((Vout / DPRESS_VREF) - 0.04) / 0.00369      #divide by 0018 for dPress500
#            print "Pressure:", pressure
#    time.sleep(.1)