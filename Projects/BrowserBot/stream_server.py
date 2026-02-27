#!/usr/bin/env python3
###############################################################################################################
# Program Name: Browser_Client_Coder.html
# ================================
# This code is for controlling a robot by a web browser using web sockets
# http://www.dexterindustries.com/
# History
# ------------------------------------------------
# Author     Comments
# Joshwa     Initial Authoring
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
###############################################################################################################

# CONNECTIONS-
# 	Left Motor  - Port A
# 	Right Motor - Port D
#
# PREREQUISITES
#	Tornado Web Server for Python
#
# TROUBLESHOOTING:
#	Don't use Ctrl+Z to stop the program, use Ctrl+c.
#	If you use Ctrl+Z, it will not close the socket and you won't be able to run the program the next time.
#	If you get the following error:
#		"socket.error: [Errno 98] Address already in use "
#	Run this on the terminal:
#		"sudo netstat -ap |grep :9093"
#	Note down the PID of the process running it
#	And kill that process using:
#		"kill pid"
#	If it does not work use:
#		"kill -9 pid"
#	If the error does not go away, try changin the port number '9093' both in the client and server code

import asyncio
import brickpi3 #import BrickPi3.py file to use BrickPi3 operations
BP = brickpi3.BrickPi3()
import threading
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template
import camera_streamer
import time

cameraStreamer = camera_streamer.CameraStreamer()
c=0
global left_power
global right_power
right_power = 0
left_power = 0

#Initialize TOrnado to use 'GET' and load index.html
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        loader = tornado.template.Loader(".")
        self.write(loader.load("index.html").generate())

#Code for handling the data sent from the webpage
class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print('connection opened...')
        cameraStreamer.startStreaming()  # no-op if already started
        # Stream JPEG frames as binary WebSocket messages so any browser
        # can display them regardless of mixed-content/HTTPS-Only restrictions.
        tornado.ioloop.IOLoop.current().spawn_callback(self.send_frames)

    async def send_frames(self):
        """Push individual JPEG frames to this WebSocket client as binary messages."""
        output = cameraStreamer.output
        if output is None:
            return
        loop = asyncio.get_running_loop()
        def _wait_frame():
            with output.condition:
                output.condition.wait(timeout=5)
                return output.frame
        try:
            while True:
                frame = await loop.run_in_executor(None, _wait_frame)
                if frame is None:
                    continue
                self.write_message(frame, binary=True)
        except tornado.websocket.WebSocketClosedError:
            pass
        except Exception as e:
            print(f'send_frames ended: {e}')

    def check_origin(self,origin):
        return True
    def on_message(self, message):      # receives the data from the webpage and is stored in the variable message
        global c
        global left_power
        global right_power
        cameraStreamer.update()
        print(f'received: {message}')        # prints the revived from the webpage
        if message == "u":                # checks for the received data and assigns different values to c which controls the movement of robot.
            c = "8";
        if message == "d":
            c = "2"
        if message == "l":
            c = "6"
        if message == "r":
            c = "4"
        if message == "b":
            c = "5"
        if message == "lu":
            c = "7"
        if message == "ru":
            c = "9"
        if message == "ld":
            c = "1"
        if message == "rd":
            c = "3"
        print(f'{c}')
        if c == '8' :
            print('Running Forward')
            # first check which side has higher power and set it to the lowest setting before increasing it
            if right_power > left_power:
                right_power = left_power
            if left_power > right_power:
                left_power = right_power
            right_power = right_power + 50
            if right_power > 255:
                right_power = 255
            left_power = right_power
            BP.set_motor_power(BP.PORT_B, left_power)  #Set the speed of MotorB (-255 to 255)
            BP.set_motor_power(BP.PORT_D, right_power)  #Set the speed of MotorD (-255 to 255)
        elif c == '2' :
            print('Running Reverse')
            # first check which side has lower power and set it to the lowest setting before increasing it
            if right_power < left_power:
                right_power = left_power
            if left_power < right_power:
                left_power = right_power
            right_power = right_power - 50
            if right_power < -255:
                right_power = -255
            left_power = right_power
            BP.set_motor_power(BP.PORT_B, left_power)
            BP.set_motor_power(BP.PORT_D, right_power)
        elif c == '4' :
            print('Turning Left')
            left_power = left_power + 100
            right_power = 0
            if left_power > 255:
                left_power = 255
            BP.set_motor_power(BP.PORT_B, left_power)
            BP.set_motor_power(BP.PORT_D, right_power)
        elif c == '7' :
            print('Turning diagonal Left')
            if right_power > 200:
                right_power = 100
            right_power = right_power + 50
            left_power = right_power // 2
            if right_power > 255:
                right_power = 255
            BP.set_motor_power(BP.PORT_B, left_power)
            BP.set_motor_power(BP.PORT_D, right_power)
        elif c == '6' :
            print('Turning Right')
            right_power = right_power + 100
            left_power = 0
            if right_power > 255:
                right_power = 255
            BP.set_motor_power(BP.PORT_B, left_power)
            BP.set_motor_power(BP.PORT_D, right_power)
        elif c == '9' :
            print('Turning diagonal Right')
            if left_power > 200:
                left_power = 100
            left_power = left_power + 50
            right_power = left_power // 2
            if left_power > 255:
                left_power = 255
            BP.set_motor_power(BP.PORT_B, left_power)
            BP.set_motor_power(BP.PORT_D, right_power)
        elif c == '5' :
            print('Stopped')
            right_power = 0
            left_power = 0
            BP.set_motor_power(BP.PORT_B, left_power)
            BP.set_motor_power(BP.PORT_D, right_power)
        print('Values Updated')
    def on_close(self):
        cameraStreamer.stopStreaming()
        print('connection closed...')

application = tornado.web.Application([
    (r'/ws', WSHandler),
    (r'/stream', camera_streamer.MJPEGHandler, {'camera_streamer': cameraStreamer}),
    (r'/', MainHandler),
    (r'/streaming_client.html', tornado.web.StaticFileHandler, {'path': './streaming_client.html'}),
    (r"/(.*)", tornado.web.StaticFileHandler, {"path": "./resources"}),
])

class myThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        print('Ready')
        while running:
            time.sleep(.2)              # sleep for 200 ms
        cameraStreamer.stopStreaming()

if __name__ == "__main__":
    running = True
    cameraStreamer.startStreaming()     # start camera immediately so /stream is ready
    thread1 = myThread(1, "Thread-1", 1)
    thread1.daemon = True
    thread1.start()
    application.listen(9093)          	#starts the websockets connection

    tornado.ioloop.IOLoop.current().start()


