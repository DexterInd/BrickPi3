from BrickPi3Scratch import *

test_msgs = []
test_msgs += ["S1 EV3US",
    "S2EV3TOUCH",
    "S3  ULTRASONIC",
    "S4 TEMP "]
test_msgs += ["S1",
    "S2",
    "S3",
    "S4"]
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
test_msgs += ["Update"]


def test_regex():
    for test_str in test_msgs:
        assert(is_BrickPi_msg(test_str))

if __name__ == '__main__':

    test_regex()

    handle_BrickPi_msg("S2TOUCH")
    handle_BrickPi_msg("S2 EV3US")
    handle_BrickPi_msg("S2 EV3USCM")
    handle_BrickPi_msg("S2 EV3USIN")
    handle_BrickPi_msg("S2 EV3USLISTEN")
    handle_BrickPi_msg("S2 EV3GYRO")
    handle_BrickPi_msg("S2 EV3GYROABS")
    handle_BrickPi_msg("S2 EV3GYROABSDPS")
    handle_BrickPi_msg("S2 EV3US")
    handle_BrickPi_msg("S2 EV3IR")
    handle_BrickPi_msg("S2 EV3IRPROX")
    handle_BrickPi_msg("S2 EV3TOUCH")
    handle_BrickPi_msg("S2 EV3COLOR")
    handle_BrickPi_msg("S2 NXTUS")
    handle_BrickPi_msg("S2 ULTRASONIC")
    handle_BrickPi_msg("S2 NXTTOUCH")
    handle_BrickPi_msg("S2 TOUCH")
    handle_BrickPi_msg("S2 NXTCOLOR")
    handle_BrickPi_msg("S2 COLOR")
    handle_BrickPi_msg("S2 RAW")
    handle_BrickPi_msg("S2 FLEX")