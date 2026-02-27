#!/usr/bin/env python3
##############################################################################################################
# This example is for streaming video and controlling the GoPiGo from a web browser
# http://www.dexterindustries.com/GoPiGo/
# History
# ------------------------------------------------
# Author     Date      		Comments
# Karan      24 July 14  	Initial Authoring
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# This example is derived from the Dawn Robotics Raspberry Pi Camera Bot
# https://bitbucket.org/DawnRobotics/raspberry_pi_camera_bot
#############################################################################################################

# Copyright (c) 2014, Dawn Robotics Ltd
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.

# 3. Neither the name of the Dawn Robotics Ltd nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import asyncio
import io
import logging
import threading

import tornado.iostream
import tornado.web

# picamera2 is pre-installed on Raspberry Pi OS Trixie:
#   sudo apt install python3-picamera2   (if missing)
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)s %(levelname)s: %(message)s')

STREAM_WIDTH  = 320
STREAM_HEIGHT = 240
STREAM_FPS    = 15

# Log detected cameras at import time so issues are visible immediately
_detected_cameras = Picamera2.global_camera_info()
if _detected_cameras:
    for _i, _cam in enumerate(_detected_cameras):
        log.info(f"Camera {_i} detected: {_cam}")
else:
    log.warning("No cameras detected by libcamera. "
                "Check cable connection and run: libcamera-hello --list-cameras")


# ---------------------------------------------------------------------------
class _StreamingOutput(io.BufferedIOBase):
    """Thread-safe buffer that holds the most-recent JPEG frame."""

    def __init__(self):
        self.frame = None
        self.condition = threading.Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


# ---------------------------------------------------------------------------
class MJPEGHandler(tornado.web.RequestHandler):
    """Tornado request handler that pushes an MJPEG stream to the browser.

    Register it in your Tornado application like this:
        (r'/stream', camera_streamer.MJPEGHandler, {'camera_streamer': cameraStreamer})
    """

    def initialize(self, camera_streamer):
        self._cs = camera_streamer

    async def get(self):
        self.set_header('Content-Type',
                        'multipart/x-mixed-replace; boundary=frame')
        self.set_header('Cache-Control', 'no-cache')
        self.set_header('Pragma', 'no-cache')
        self.set_header('Access-Control-Allow-Origin', '*')

        output = self._cs.output
        if output is None:
            self.set_status(503, 'Stream not started')
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
                self.write(b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n')
                self.write(frame)
                self.write(b'\r\n')
                await self.flush()
        except tornado.iostream.StreamClosedError:
            pass


# ---------------------------------------------------------------------------
class CameraStreamer:
    """Manages a picamera2 MJPEG capture session.

    Call startStreaming() when the first WebSocket client connects and
    stopStreaming() when the last one disconnects.  The MJPEG frames are
    served by MJPEGHandler over the existing Tornado server at /stream.
    """

    #-----------------------------------------------------------------------------------------------
    def __init__( self ):
        self.camera = None
        self.output = None
        self._started = False

    #-----------------------------------------------------------------------------------------------
    def __del__( self ):
        self.stopStreaming()

    #-----------------------------------------------------------------------------------------------
    def startStreaming( self ):
        if self._started:
            return
        cameras = Picamera2.global_camera_info()
        if not cameras:
            log.warning("No camera detected — streaming disabled.")
            return
        self.output = _StreamingOutput()
        self.camera = Picamera2()
        config = self.camera.create_video_configuration(
            main={"size": (STREAM_WIDTH, STREAM_HEIGHT)},
            controls={"FrameRate": STREAM_FPS},
        )
        self.camera.configure(config)
        self.camera.start_recording(MJPEGEncoder(), FileOutput(self.output))
        self._started = True
        log.info("Camera streaming started")

    #-----------------------------------------------------------------------------------------------
    def update( self ):
        pass  # no external process to poll; camera runs until stopStreaming()

    #-----------------------------------------------------------------------------------------------
    def stopStreaming( self ):
        if not self._started:
            return
        try:
            self.camera.stop_recording()
            self.camera.close()
        except Exception as exc:
            log.warning(f"Error stopping camera: {exc}")
        self.camera = None
        self.output = None
        self._started = False
        log.info("Camera streaming stopped")
