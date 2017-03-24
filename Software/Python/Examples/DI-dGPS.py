#!/usr/bin/env python
#
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
# This code is an example for reading a Dexter Industries GPS connected to the BrickPi3
# 
# Hardware: Connect a Dexter Industries dGPS to sensor port 1 of the BrickPi3.
# 
# Results:  When you run this program, the GPS is read, and the values are printed.

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

GPS_PORT = BP.PORT_1 # GPS will be on sensor port 1

BP.set_sensor_type(GPS_PORT, BP.SENSOR_TYPE.I2C, [BP.SENSOR_I2C_SETTINGS.MID_CLOCK, 0]) # Configure for a Dexter Industries GPS (I2C device with clock pulse between the write and read bytes).

DGPS_I2C_ADDR   = 0x06      # dGPS Sensor I2C Address 
DGPS_CMD_UTC    = 0x00      # Fetch UTC 
DGPS_CMD_STATUS = 0x01      # Status of satellite link: 0 no link, 1 link 
DGPS_CMD_LAT    = 0x02      # Fetch Latitude 
DGPS_CMD_LONG   = 0x04      # Fetch Longitude 
DGPS_CMD_VELO   = 0x06      # Fetch velocity in cm/s 
DGPS_CMD_HEAD   = 0x07      # Fetch heading in degrees 
DGPS_CMD_DIST   = 0x08		# Fetch distance to destination
DGPS_CMD_ANGD   = 0x09      # Fetch angle to destination 
DGPS_CMD_ANGR   = 0x0A      # Fetch angle travelled since last request
DGPS_CMD_SLAT   = 0x0B      # Set latitude of destination 
DGPS_CMD_SLONG  = 0x0C      # Set longitude of destination
DGPS_CMD_XFIRM  = 0x0D	    # Extended firmware
DGPS_CMD_ALTTD  = 0x0E	    # Altitude
DGPS_CMD_HDOP   = 0x0F	    # HDOP
DGPS_CMD_VWSAT  = 0x10	    # Satellites in View

try:
    while True:
        try:
            BP.transact_i2c(GPS_PORT, DGPS_I2C_ADDR, [DGPS_CMD_UTC], 4)
            time.sleep(0.02)          # delay 20ms
            value = BP.get_sensor(GPS_PORT) # read the sensor values
            
            UTC = ((long)(value[0]<<24)) + ((long)(value[1]<<16)) + ((long)(value[2]<<8)) + (long)(value[3])
            
            BP.transact_i2c(GPS_PORT, DGPS_I2C_ADDR, [DGPS_CMD_LONG], 4)
            time.sleep(0.02)          # delay 20ms
            value = BP.get_sensor(GPS_PORT) # read the sensor values
            
            lon = ((long)(value[0]<<24)) + ((long)(value[1]<<16)) + ((long)(value[2]<<8)) + (long)(value[3])
            if value[0]>10:	#if the 0th byte >10, then the longitude was negative and use the 2's compliment of the longitude
                lon=(4294967295L^lon)+1
                lon=(-float(lon)/1000000)
            else:
                lon=(float(lon)/1000000)
            
            BP.transact_i2c(GPS_PORT, DGPS_I2C_ADDR, [DGPS_CMD_LAT], 4)
            time.sleep(0.02)          # delay 20ms
            value = BP.get_sensor(GPS_PORT) # read the sensor values
            
            lat = ((long)(value[0]<<24)) + ((long)(value[1]<<16)) + ((long)(value[2]<<8)) + (long)(value[3])
            if value[0]>10:	#if the 0th byte >10, then the longitude was negative and use the 2's compliment of the longitude
                lat=(4294967295L^lat)+1
                lat=(-float(lat)/1000000)
            else:
                lat=(float(lat)/1000000)
            
            BP.transact_i2c(GPS_PORT, DGPS_I2C_ADDR, [DGPS_CMD_HEAD], 2)
            time.sleep(0.02)          # delay 20ms
            value = BP.get_sensor(GPS_PORT) # read the sensor values
            
            head = ((long)(value[0]<<8)) + ((long)(value[1]))
            
            BP.transact_i2c(GPS_PORT, DGPS_I2C_ADDR, [DGPS_CMD_STATUS], 1)
            time.sleep(0.02)          # delay 20ms
            value = BP.get_sensor(GPS_PORT) # read the sensor values
            
            status = (long)(value[0])
            
            BP.transact_i2c(GPS_PORT, DGPS_I2C_ADDR, [DGPS_CMD_VELO], 3)
            time.sleep(0.02)          # delay 20ms
            value = BP.get_sensor(GPS_PORT) # read the sensor values
            
            velo = ((long)(value[0]<<16)) + ((long)(value[1]<<8)) + (long)(value[2])
            
            BP.transact_i2c(GPS_PORT, DGPS_I2C_ADDR, [DGPS_CMD_ALTTD], 4)
            time.sleep(0.02)          # delay 20ms
            value = BP.get_sensor(GPS_PORT) # read the sensor values
            
            altitude = ((long)(value[0]<<24)) + ((long)(value[1]<<16)) + ((long)(value[2]<<8)) + (long)(value[3])
            
            BP.transact_i2c(GPS_PORT, DGPS_I2C_ADDR, [DGPS_CMD_HDOP], 4)
            time.sleep(0.02)          # delay 20ms
            value = BP.get_sensor(GPS_PORT) # read the sensor values
            
            hdop = ((long)(value[0]<<24)) + ((long)(value[1]<<16)) + ((long)(value[2]<<8)) + (long)(value[3])
            
            BP.transact_i2c(GPS_PORT, DGPS_I2C_ADDR, [DGPS_CMD_VWSAT], 4)
            time.sleep(0.02)          # delay 20ms
            value = BP.get_sensor(GPS_PORT) # read the sensor values
            
            satv = ((long)(value[0]<<24)) + ((long)(value[1]<<16)) + ((long)(value[2]<<8)) + (long)(value[3])
            
            print('Status',status,'UTC',UTC,'Latitude %.6f'% lat,'Longitude %.6f'%lon,'Heading',head,'Velocity',velo,'Altitude',altitude,'HDOP',hdop,'Satellites in view',satv)
        
        except brickpi3.SensorError as error:
            print(error)
        
except KeyboardInterrupt:
    BP.reset_all()