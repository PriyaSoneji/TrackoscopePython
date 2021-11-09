# make sure bluetooth is off
import tkinter as tk
from tkinter import *
from PIL import Image
from PIL import ImageTk
import imutils
import threading
import cv2
from time import sleep
import serial
import pyautogui
import pandas
import glob
import numpy as np
from imutils.video import VideoStream
from imutils.video import FPS
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
from src_new.arduino_communication import *
from src_new.trajectory_mapping import *
from src_new.gui import *
from src_new.zaxis import *

# define tracking variables
x = 0
y = 0
w = 0
h = 0
W = 0
H = 0

# define stuff for x-coordinate detection
ovcenterx = 0
smallx = 0
largex = 0
oldxdirection = 'N'
newxdirection = 'N'
xdirection = 'N'
centerx = 0

# define stuff for y-coordinate detection
ovcentery = 0
smally = 0
largey = 0
oldydirection = 'N'
newydirection = 'N'
ydirection = 'N'
centery = 0

# range limits
xrangehl = 60
xrangell = 40
yrangehl = 60
yrangell = 40

# graphing stuff
currx = 0
curry = 0

x_values = []
y_values = []

x_values.append(0)
y_values.append(0)

# the micrometers per send
basestepsize = 86.24
incrementstepxy = basestepsize / 2

# function to create our object tracker
tracker = cv2.TrackerCSRT_create()

# initialize the bounding box coordinates
initBB = None

fps = FPS().start()
infovar = StringVar()


def videoLoop(vs):
    global panelB, frame, initBB, x, y, w, h, H, W, centered, fps, trackingsuccess, centerx, centery, showOverlay, oldxdirection, oldydirection
    try:
        # keep looping over frames until we are instructed to stop
        while not stopEvent.is_set():
            # grab the frame from the video stream and resize it to
            # have a maximum width of 300 pixels
            frame = vs.read()
            frame = imutils.resize(frame, width=700)
            (H, W) = frame.shape[:2]

            # check to see if we are currently tracking an object
            if initBB is not None:
                # grab the new bounding box coordinates of the object
                (success, box) = tracker.update(frame)
                (x, y, w, h) = [int(v) for v in box]

                trackingsuccess = success
                centerx = x + int(w / 2)
                centery = y + int(h / 2)

                if centerx > 585 or centerx < 15:
                    trackingsuccess = bool(False)
                if centery > 435 or centery < 15:
                    trackingsuccess = bool(False)

                if not trackingsuccess:
                    (success, box) = tracker.update(frame)
                    (x, y, w, h) = [int(v) for v in box]
                    sendCommand('S'.encode())
                    oldxdirection = 'X'
                    oldydirection = 'Y'

                if not success:
                    infovar.set("Tracking Unsuccessful")

                if success:
                    centered = makemove()

                    # cv2.rectangle(frame, (x, y), (x + w, y + h),
                    #               (0, 255, 0), 2)

                    if showOverlay:
                        if centered:
                            cv2.circle(frame, (x + int(w / 2), y + int(h / 2)), 1, (0, 255, 0), 2)
                        else:
                            cv2.circle(frame, (x + int(w / 2), y + int(h / 2)), 1, (0, 0, 255), 2)

            fps.update()
            fps.stop()

            now = datetime.datetime.now()
            timestamp = str(now.strftime("%H:%M:%S"))

            # initialize info on screen
            info = [
                ("Time", timestamp)
                # ("FPS", "{:.2f}".format(fps.fps())),
                # ("X-Move", oldxdirection),
                # ("Y-Move", oldydirection),
            ]

            for (i, (k, v)) in enumerate(info):
                text = "{}: {}".format(k, v)
                cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            # Put Video source in Tkinter format
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            image = ImageTk.PhotoImage(image)

            # if the panel is not None, we need to initialize it
            if panelB is None:
                panelB = tk.Label(image=image)
                panelB.image = image
                panelB.grid(row=0, column=0)

            # otherwise, simply update the panel
            else:
                panelB.configure(image=image)
                panelB.image = image

    except RuntimeError:
        print("[INFO] caught a RuntimeError")


# defines how to make a move depending on location of bounding box center
def makemove():
    global centerx, centery, newxdirection, oldxdirection, newydirection, oldydirection, ydirection, \
        xdirection, x, y, w, h, W, H, currx, curry, centered, incrementstepxy, trackingsuccess, speedMode

    centerx = x + int(w / 2)
    centery = y + int(h / 2)

    # Send X direction
    if ((centerx / W) * 100) > xrangehl:
        newxdirection = 'R'
        currx = currx + incrementstepxy
        addpoint()
    elif ((centerx / W) * 100) < xrangell:
        newxdirection = 'L'
        currx = currx - incrementstepxy
        addpoint()
    else:
        newxdirection = 'X'

    if oldxdirection != newxdirection:
        sendCommand(newxdirection.encode())
        oldxdirection = newxdirection

    # Send Y direction
    if ((centery / H) * 100) > yrangehl:
        newydirection = 'U'
        curry = curry - incrementstepxy
        addpoint()
    elif ((centery / H) * 100) < yrangell:
        newydirection = 'D'
        curry = curry + incrementstepxy
        addpoint()
    else:
        newydirection = 'Y'

    if oldydirection != newydirection:
        sendCommand(newydirection.encode())
        oldydirection = newydirection

    if not trackingsuccess:
        oldydirection = 'Y'
        oldxdirection = 'X'

    if (newydirection == 'Y') and (newxdirection == 'X'):
        if not speedMode:
            sendCommand('E'.encode())
        centered = True
    else:
        centered = False

    if abs(currx) > 100000 or abs(curry) > 100000:
        hardStop()
        dataSave()
        onClose()

    return centered


# starts tracking and prompts user to select the object that they wish to track
def startTracking():
    global frame, initBB, tracker, tracking, thread2, ser1, infovar
    # if the 's' key is selected start tracking
    initBB = cv2.selectROI('Selection', frame, showCrosshair=True)
    cv2.destroyWindow('Selection')
    # start OpenCV object tracker using the supplied bounding box
    tracker.init(frame, initBB)
    ser1.flush()

    if trackinginZ:
        thread2.start()

    infovar.set("Tracking Started")

    tracking = True


def get_x_vals():
    return x_values


def get_y_vals():
    return y_values


def add_x_val(val):
    x_values.append(val)


def add_y_val(val):
    y_values.append(val)
