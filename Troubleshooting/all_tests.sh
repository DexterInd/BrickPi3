#! /bin/bash

cd /home/pi/Dexter/BrickPi3/Troubleshooting/

echo "==============================="
echo "BrickPi3 Troubleshooting Script"
echo "==============================="

echo "BrickPi3 Troubleshooting Script log" > log.txt
#sudo ./software_status.sh 2>&1| tee log.txt
#sudo ./avrdude_test.sh 2>&1| tee -a log.txt
#sudo ./i2c_test1.sh 2>&1| tee -a log.txt
sudo bash hardware_and_firmware_test.sh 2>&1| tee -a log.txt
#sudo ./motor_enc_led_test.sh 2>&1| tee -a log.txt

echo ""
cp log.txt /home/pi/Desktop/log.txt
echo "Log has been saved to Desktop. Please copy it and send it by email or upload it on the forums"
