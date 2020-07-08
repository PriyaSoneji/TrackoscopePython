# import the necessary packages
from imutils.video import FPS
import argparse
import imutils
import threading
import time
from imutils.video import VideoStream
from imutils.video.pivideostream import PiVideoStream
import cv2
import serial
from time import sleep

# open Arduino Serial
ser1 = serial.Serial('/dev/ttyACM0', 115200)
ser1.flush()
sleep(2)
portopen = True

# start video stream
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
sleep(2.0)

# initialize the FPS throughput estimator
fps = None

# loop over frames from the video stream
while True:
    frame = vs.read()
    frame = imutils.resize(frame, width=800)
    (H, W) = frame.shape[:2]
    ovcenterx = W / 2
    # check to see if we are currently tracking an object
    # update the FPS counter
    fps.update()
    fps.stop()

    # initialize info on screen
    info = [
        ("FPS", "{:.2f}".format(fps.fps()))
    ]
    for (i, (k, v)) in enumerate(info):
        text = "{}: {}".format(k, v)
        cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

# close all windows
cv2.destroyAllWindows()
