#!/usr/bin/env python3
###############################################################################################################
# Program Name: Browser_Client_Coder.html
# ================================
# This code is for controlling a robot by a web browser using web sockets
# http://www.dexterindustries.com/
# History
# ------------------------------------------------#
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

import brickpi3  # import BrickPi3.py file to use BrickPi3 operations
BP = brickpi3.BrickPi3()
import time
import threading
try:
    import tornado.ioloop
    import tornado.web
    import tornado.websocket
    import tornado.template
except ImportError:
    print("Error: The 'tornado' package is required. Install it with:\n    pip install tornado")
    exit(1)

c = 0
# Initialize Tornado to use 'GET' and load index.html
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        loader = tornado.template.Loader(".")
        self.write(loader.load("index.html").generate())

# Code for handling the data sent from the webpage
class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print('connection opened...')
    def check_origin(self, origin):
        return True
    def on_message(self, message):  # receives the data from the webpage and is stored in the variable message
        global c
        print(f'received: {message}')  # prints the received data from the webpage
        if message == "u":
            c = "8"
        elif message == "d":
            c = "2"
        elif message == "l":
            c = "6"
        elif message == "r":
            c = "4"
        elif message == "b":
            c = "5"
        print(f'{c}')
        if c == '8':
            print("Running Forward")
            BP.set_motor_power(BP.PORT_A, 200)
            BP.set_motor_power(BP.PORT_D, 200)
        elif c == '2':
            print("Running Reverse")
            BP.set_motor_power(BP.PORT_A, -200)
            BP.set_motor_power(BP.PORT_D, -200)
        elif c == '4':
            print("Turning Right")
            BP.set_motor_power(BP.PORT_A, 200)
            BP.set_motor_power(BP.PORT_D, 0)
        elif c == '6':
            print("Turning Left")
            BP.set_motor_power(BP.PORT_A, 0)
            BP.set_motor_power(BP.PORT_D, 200)
        elif c == '5':
            print("Stopped")
            BP.set_motor_power(BP.PORT_A, 0)
            BP.set_motor_power(BP.PORT_D, 0)
    def on_close(self):
        print('connection closed...')

application = tornado.web.Application([
    (r'/ws', WSHandler),
    (r'/', MainHandler),
    (r"/(.*)", tornado.web.StaticFileHandler, {"path": "./resources"}),
])

class MyThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        super().__init__()
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        print("Ready")
        while running:
            time.sleep(0.2)  # sleep for 200 ms

if __name__ == "__main__":
    running = True
    thread1 = MyThread(1, "Thread-1", 1)
    thread1.daemon = True
    thread1.start()
    application.listen(9093)  # starts the websockets connection
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        print("\nShutting down server and stopping motors.")
        BP.set_motor_power(BP.PORT_A, 0)
        BP.set_motor_power(BP.PORT_D, 0)
        tornado.ioloop.IOLoop.current().stop()
        exit(0)


