import tkinter as tk
from tkinter import *
from PIL import Image
from PIL import ImageTk
import imutils
import threading
import argparse
import cv2
import time
from time import sleep
import serial
import glob
from imutils.video import VideoStream
from imutils.video import FPS
from pandas import DataFrame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

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

# flipping variables
portopen = bool(False)
horizder = bool(False)
vertder = bool(False)
rotate = bool(False)
sendrepeat = bool(False)
centered = bool(False)
cameramode = bool(True)
tracking = bool(False)

# range limits
xrangehl = 55
xrangell = 45
yrangehl = 55
yrangell = 45
xrangehs = 60
xrangels = 40
yrangehs = 60
yrangels = 40
availvid = []

# graphing stuff
currx = 0
curry = 0
count = 0
steptodistance = 1
countmax = 10

x_values = []
y_values = []

x_values.append(0)
y_values.append(0)


# button press commands
def swapHorizontal():
    global horizder
    horizder = not horizder


def swapVertical():
    global vertder
    vertder = not vertder


def swapMode():
    global cameramode
    cameramode = not cameramode


def quitTracking():
    global initBB
    cv2.destroyAllWindows()
    sendCommand('S'.encode())
    vs.stop()
    initBB = None


def savePlot():
    figure1.savefig('output.png')


def home():
    if cameramode:
        if currx > 0 and currx > 70:
            print("moving back")


# initialize the window toolkit along with the two image panels
root = Tk()
panelA = None
panelB = None
frame = None
thread = None
stopEvent = None
stopEvent = threading.Event()


# add points to the graph and updates plot
def addpoint():
    global count, countmax, figure1
    if count == countmax:
        x_values.append(currx * steptodistance)
        y_values.append(curry * steptodistance)
        count = 0
    count = count + 1


# check for available serial ports
def serial_ports():
    # List serial ports
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(50)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


# open Arduino Serial
availableport = serial_ports()
if len(availableport) > 0:
    ser1 = serial.Serial(availableport[0], 115200)
    sleep(2)
    portopen = True

# construct the argument parser for opencv and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str,
                help="path to input video file")
ap.add_argument("-t", "--tracker", type=str, default="csrt",
                help="OpenCV object tracker type")
args = vars(ap.parse_args())

# extract the OpenCV version info
(major, minor) = cv2.__version__.split(".")[:2]

# function to create our object tracker
if int(major) == 3 and int(minor) < 3:
    tracker = cv2.Tracker_create(args["tracker"].upper())
else:
    # OpenCV object tracker implementations
    OPENCV_OBJECT_TRACKERS = {
        "csrt": cv2.TrackerCSRT_create,
        "kcf": cv2.TrackerKCF_create,
        "boosting": cv2.TrackerBoosting_create,
        "mil": cv2.TrackerMIL_create,
        "tld": cv2.TrackerTLD_create,
        "medianflow": cv2.TrackerMedianFlow_create,
        "mosse": cv2.TrackerMOSSE_create
    }
    # OpenCV object tracker objects
    tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()

# initialize the bounding box coordinates
initBB = None


# sends command to the Arduino over serial port
def sendCommand(cmd):
    if portopen:
        ser1.write(cmd)
        # sleep(0.4)
        # if not centered:
        #     ser1.write(cmd)


fps = None


def videoLoop():
    global vs, panelB, frame, initBB, x, y, w, h, H, W, centered, fps
    try:
        # keep looping over frames until we are instructed to stop
        while not stopEvent.is_set():
            # grab the frame from the video stream and resize it to
            # have a maximum width of 300 pixels
            frame = vs.read()
            frame = imutils.resize(frame, width=600)
            (H, W) = frame.shape[:2]
            # check to see if we are currently tracking an object
            if initBB is not None:
                # grab the new bounding box coordinates of the object
                (success, box) = tracker.update(frame)
                if success:
                    (x, y, w, h) = [int(v) for v in box]
                    cv2.rectangle(frame, (x, y), (x + w, y + h),
                                  (0, 255, 0), 2)
                    centered = makemove()
                else:
                    sendCommand('S'.encode())

                fps.update()
                fps.stop()

                # initialize info on screen
                info = [
                    ("FPS", "{:.2f}".format(fps.fps())),
                    ("X-Move", oldxdirection),
                    ("Y-Move", oldydirection),
                    ("In Center", "Yes" if centered else "No"),
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
    global smallx, largex, centerx, smally, largey, centery, newxdirection, oldxdirection, newydirection, \
        oldydirection, ydirection, xdirection, x, y, w, h, W, H, currx, curry
    smallx = x
    largex = x + w
    centerx = (smallx + largex) / 2
    smally = y
    largey = y + h
    centery = (smally + largey) / 2

    # large movements
    if cameramode:
        # Send X direction
        if ((centerx / W) * 100) > xrangehl:
            if horizder:
                newxdirection = 'L'
                currx = currx - 1
                addpoint()
            else:
                newxdirection = 'R'
                currx = currx + 1
                addpoint()
        elif ((centerx / W) * 100) < xrangell:
            if horizder:
                newxdirection = 'R'
                currx = currx + 1
                addpoint()
            else:
                newxdirection = 'L'
                currx = currx - 1
                addpoint()
        else:
            newxdirection = 'X'
        if (oldxdirection != newxdirection) or sendrepeat:
            sendCommand(newxdirection.encode())
            oldxdirection = newxdirection

        # Send Y direction
        if ((centery / H) * 100) > yrangehl:
            if vertder:
                newydirection = 'D'
                curry = curry + 1
                addpoint()
            else:
                newydirection = 'U'
                curry = curry - 1
                addpoint()
        elif ((centery / H) * 100) < yrangell:
            if vertder:
                newydirection = 'U'
                curry = curry - 1
                addpoint()
            else:
                newydirection = 'D'
                curry = curry + 1
                addpoint()
        else:
            newydirection = 'Y'
        if (oldydirection != newydirection) or sendrepeat:
            sendCommand(newydirection.encode())
            oldydirection = newydirection

    # small movements
    if not cameramode:
        # Send X direction
        if ((centerx / W) * 100) > xrangehs:
            if horizder:
                xdirection = 'l'
                currx = currx + 1
                addpoint()

            else:
                xdirection = 'r'
                currx = currx - 1
                addpoint()

        elif ((centerx / W) * 100) < xrangels:
            if horizder:
                xdirection = 'r'
                currx = currx - 1
                addpoint()

            else:
                xdirection = 'l'
                currx = currx + 1
                addpoint()

        else:
            xdirection = 'x'
        if (xdirection != 'x') or sendrepeat:
            sendCommand(xdirection.encode())
        # Send Y direction
        if ((centery / H) * 100) > yrangehs:
            if vertder:
                ydirection = 'd'
                curry = curry + 1
                addpoint()

            else:
                ydirection = 'u'
                curry = curry - 1
                addpoint()

        elif ((centery / H) * 100) < yrangels:
            if vertder:
                ydirection = 'u'
                curry = curry - 1
                addpoint()

            else:
                ydirection = 'd'
                curry = curry + 1
                addpoint()

        else:
            ydirection = 'y'

        if (ydirection != 'y') or sendrepeat:
            sendCommand(ydirection.encode())

    if ((newydirection == 'Y') and (newxdirection == 'X')) or ((ydirection == 'y') and (xdirection == 'x')):
        centered = True
    else:
        centered = False
    return centered


# allows for the manual control of the platform
def manualmove():
    global currx, curry, key

    if key == '5':
        sendCommand('S'.encode())
    if key == '8':
        print("Up/Down")
        if vertder:
            sendCommand('u'.encode())

        else:
            sendCommand('d'.encode())

    if key == '2':
        print("Up/Down")
        if vertder:
            sendCommand('d'.encode())

        else:
            sendCommand('u'.encode())

    if key == '4':
        print("Left/Right")
        if horizder:
            sendCommand('r'.encode())

        else:
            sendCommand('l'.encode())

    if key == '6':
        print("Left/Right")
        if horizder:
            sendCommand('l'.encode())

        else:
            sendCommand('r'.encode())


# figure one data
df1 = None
figure1 = plt.Figure(figsize=(6, 5), dpi=100)
ax = figure1.add_subplot(111)
bar1 = FigureCanvasTkAgg(figure1, root)
bar1.get_tk_widget().grid(row=0, column=1)


def plotgraph():
    # grab a reference to the image panels
    global panelA, df1, figure1, ax, root
    # data for the plot
    df1 = DataFrame({'X-Movement': x_values,
                     'Y-Movement': y_values})
    df1.plot(kind='line', legend=False, ax=ax, grid=True, x='X-Movement', y='Y-Movement', title="Protist Trajectory")
    df1.plot(kind='scatter', legend=False, ax=ax, grid=True, x='X-Movement', y='Y-Movement', title="Protist Trajectory")
    # root.update()
    bar1.draw_idle()


# Checks for a valid camera
def testDevice(source):
    print("Trying video source", source)
    cap = cv2.VideoCapture(source)
    if cap is None or not cap.isOpened():
        return False
    else:
        return True


# get keys
key = None


def up(e):
    global key
    key = e.char
    print(key)
    manualmove()


def startTracking():
    global frame, initBB, tracker, tracking, fps
    # if the 's' key is selected start tracking
    initBB = cv2.selectROI("Frame", frame, fromCenter=False,
                           showCrosshair=True)

    # start OpenCV object tracker using the supplied bounding box
    tracker.init(frame, initBB)
    fps = FPS().start()

    tracking = True


startButton = Button(root, text="Start Tracking", command=startTracking, activebackground='yellow')
plotButton = Button(root, text="Plot Graph", command=plotgraph, activebackground='yellow')
hFlipButton = Button(root, text="Flip Horizontal Direction", command=swapHorizontal, activebackground='yellow')
vFlipButton = Button(root, text="Flip Vertical Direction", command=swapVertical, activebackground='yellow')
modeButton = Button(root, text="Change Operating Mode", command=swapMode, activebackground='yellow')
stopButton = Button(root, text="Quit the Program", command=quitTracking, activebackground='yellow')
saveButton = Button(root, text="Save Image of Plot", command=savePlot, activebackground='yellow')
homeButton = Button(root, text="Auto-Home", command=home, activebackground='yellow')

root.bind('<KeyRelease>', up)

# if a video path was not supplied, grab the reference to the web cam
if not args.get("video", False):
    print("[INFO] starting video stream...")
    for x in range(3):
        if testDevice(x):
            availvid.append(x)
    vs = VideoStream(src=(availvid[len(availvid) - 1])).start()
    sleep(1.0)
# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])

startButton.grid(row=1, column=0, sticky='WENS')
plotButton.grid(row=1, column=1, sticky='WENS')
hFlipButton.grid(row=2, column=0, sticky='WENS')
vFlipButton.grid(row=2, column=1, sticky='WENS')
modeButton.grid(row=3, column=0, sticky='WENS')
stopButton.grid(row=3, column=1, sticky='WENS')
saveButton.grid(row=4, column=0, sticky='WENS')
homeButton.grid(row=4, column=1, sticky='WENS')
thread = threading.Thread(target=videoLoop, args=())
thread.start()
# plotgraph()

# kick off the GUI
root.mainloop()
