echo "Restarting the BrickPi3 SAMD."
sudo openocd -f interface/raspberrypi2-native.cfg -c "transport select swd; set CHIPNAME at91samd21j18; source [find target/at91samdXX.cfg]; adapter_khz 100; adapter_nsrst_delay 100; adapter_nsrst_assert_width 100" -c "init; targets; reset" -c "shutdown"
