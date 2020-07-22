import tkinter as tk
from tkinter import *
from PIL import Image
from PIL import ImageTk
import imutils
import threading
import argparse
import cv2
from time import sleep
import serial
import pyautogui
import glob
import torch
import numpy as np
from imutils.video import VideoStream
from imutils.video import FPS
from pandas import DataFrame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    from control.DaSiamRPN.code.net import SiamRPNvot
    from control.DaSiamRPN.code import vot
    from control.DaSiamRPN.code.run_SiamRPN import SiamRPN_init, SiamRPN_track
    from control.DaSiamRPN.code.utils import get_axis_aligned_bbox, cxy_wh_2_rect
except ImportError:
    print('Warning: DaSiamRPN is not available!')

# define tracking type
neuralTrack = bool(False)

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
vertder = bool(True)
rotate = bool(False)
sendrepeat = bool(False)
centered = bool(False)
tracking = bool(False)

# range limits
xrangehl = 65
xrangell = 35
yrangehl = 65
yrangell = 35

# graphing stuff
currx = 0
curry = 0
count = 0
countmax = 10

# Z-Axis
zdirection = 'N'
blurry = bool(False)
rightDirection = bool(False)
focus = 0
originalFocus = 0
compareFocus = 0

x_values = []
y_values = []
z_values = []

x_values.append(0)
y_values.append(0)
z_values.append(0)

availvid = []


# checks for bluriness
def variance_of_laplacian(image):
    # compute the Laplacian of the image and then return the focus
    # measure, which is simply the variance of the Laplacian
    return cv2.Laplacian(image, cv2.CV_64F).var()


# button press commands
def swapHorizontal():
    global horizder
    horizder = not horizder


def swapVertical():
    global vertder
    vertder = not vertder


def savePlot():
    figure1.savefig('output.png')


def screenshot():
    myScreenshot = pyautogui.screenshot()
    myScreenshot.save(r'capture.png')


# initialize the window toolkit along with the two image panels
root = Tk()
panelA = None
panelB = None
frame = None
thread = None
thread2 = None
state = None
stopEvent = threading.Event()


# add points to the graph and updates plot
def addpoint():
    global count, countmax, figure1
    if count == countmax:
        x_values.append(currx)
        y_values.append(curry)
        # plotgraph()
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
    sleep(1)
    ser1.flush()
    sleep(1)
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

    NEURALNETTRACKERS = {"daSiamRPN": []}

    # OpenCV object tracker objects
    tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()

    try:
        # load net
        net = SiamRPNvot()
        net.load_state_dict(torch.load(join(realpath(dirname(__file__)), 'DaSiamRPN', 'code', 'SiamRPNBIG.model')))
        net.eval().cuda()
        print('Finished loading net ...')
        neuralTrack = bool(True)

    except:
        print('No neural net model found ...')
        print('reverting to default OpenCV tracker')
        neuralTrack = bool(False)

# initialize the bounding box coordinates
initBB = None


# def sendCommand(cmd):
#     global portopen, ser1
#     ser1.flush()
#     if portopen:
#         ser1.write(cmd)


def sendCommand(cmd):
    global portopen, ser1
    if portopen:
        thread3 = threading.Thread(target=sendCommandThread, args=(cmd, ser1))
        thread3.start()


# sends command to the Arduino over serial port
def sendCommandThread(cmd, serport):
    serport.write(cmd)
    if not centered:
        serport.write(cmd)


fps = FPS().start()


def videoLoop():
    global vs, panelB, frame, initBB, x, y, w, h, H, W, centered, fps, state
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
                if neuralTrack:
                    state = SiamRPN_track(state, frame)

                    success = True

                    if success:
                        # (x,y,w,h)
                        box = cxy_wh_2_rect(state['target_pos'], state['target_sz'])
                        box = [int(j) for j in box]

                        cv2.rectangle(frame, (box[0], box[1]), (box[0] + box[2], box[1] + box[3]), (0, 255, 255), 3)

                else:
                    (success, box) = tracker.update(frame)

                    if success:
                        (x, y, w, h) = [int(v) for v in box]
                        centered = makemove()
                        if centered:
                            cv2.rectangle(frame, (x, y), (x + w, y + h),
                                          (0, 255, 0), 2)
                        else:
                            cv2.rectangle(frame, (x, y), (x + w, y + h),
                                          (0, 0, 255), 2)

            fps.update()
            fps.stop()

            # initialize info on screen
            info = [
                ("FPS", "{:.2f}".format(fps.fps())),
                ("X-Move", oldxdirection),
                ("Y-Move", oldydirection)
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


def onClose():
    # set the stop event, cleanup the camera, and allow the rest of
    # the quit process to continue
    global initBB
    print("[INFO] closing...")
    cv2.destroyAllWindows()
    sendCommand('S'.encode())
    vs.stop()
    initBB = None
    stopEvent.set()
    root.quit()
    sys.exit()


# defines how to make a move depending on location of bounding box center
# defines how to make a move depending on location of bounding box center
def makemove():
    global smallx, largex, centerx, smally, largey, centery, newxdirection, oldxdirection, newydirection, \
        oldydirection, ydirection, xdirection, x, y, w, h, W, H, currx, curry, centered
    smallx = x
    largex = x + w
    centerx = (smallx + largex) / 2
    smally = y
    largey = y + h
    centery = (smally + largey) / 2

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

    if oldxdirection != newxdirection:
        sendCommand(newxdirection.encode())
        # ser1.flush()
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
    if oldydirection != newydirection:
        sendCommand(newydirection.encode())
        # ser1.flush()
        oldydirection = newydirection

    if (newydirection == 'Y') and (newxdirection == 'X'):
        centered = True
    else:
        centered = False

    return centered


# figure one data
figure1 = plt.Figure(figsize=(6, 5), dpi=100)
ax = figure1.add_subplot(111, projection='3d')
bar1 = FigureCanvasTkAgg(figure1, root)
bar1.get_tk_widget().grid(row=0, column=1)


def threadedZAxis():
    while not stopEvent.is_set():
        # Z-Axis Detection
        determineFocus()
        if blurry:
            fixBlurMotor()


# calculates the blur and returns the blur number
def calculateBlur():
    global focus
    image = vs.read()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    focus = round(variance_of_laplacian(gray), 2)
    return focus


# determines if it is in focus or not
def determineFocus():
    global blurry
    if calculateBlur() < 80:
        blurry = bool(True)
    else:
        blurry = bool(False)


# uses a motor to fix the blur
def fixBlurMotor():
    global originalFocus, compareFocus, rightDirection, focus, zdirection
    originalFocus = calculateBlur()
    zdirection = 'b'
    sendCommand(zdirection.encode())
    compareFocus = calculateBlur()
    if compareFocus > originalFocus:
        rightDirection = bool(True)
    else:
        rightDirection = bool(False)

    # sendCommand('S'.encode())

    if rightDirection:
        for j in range(15):
            zdirection = 'b'
            sendCommand(zdirection.encode())
            sleep(0.1)
            if calculateBlur() > 80:
                break
    else:
        for j in range(15):
            zdirection = 't'
            sendCommand(zdirection.encode())
            sleep(0.1)
            if calculateBlur() > 80:
                break

    determineFocus()
    zdirection = 'Z'
    sendCommand(zdirection.encode())


def yPos():
    sendCommand('U'.encode())


def yNeg():
    sendCommand('D'.encode())


def xPos():
    sendCommand('R'.encode())


def xNeg():
    sendCommand('L'.encode())


def zPos():
    sendCommand('T'.encode())


def zNeg():
    sendCommand('B'.encode())


def stopMov():
    sendCommand('S'.encode())


# plots the graph using matplotlib
def plotgraph():
    # grab a reference to the image panels
    global panelA, figure1, ax, root, x_values, y_values, z_values

    # plot
    ax.plot(x_values, y_values, z_values)
    ax.scatter(x_values, y_values, z_values)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # idle draw
    bar1.draw_idle()


# Checks for a valid camera
def testDevice(source):
    cap = cv2.VideoCapture(source)
    if cap is None or not cap.isOpened():
        return False
    else:
        return True


# starts tracking and prompts user to select the object that they wish to track
def startTracking():
    global frame, initBB, tracker, tracking, thread2, neuralTrack, state
    # if the 's' key is selected start tracking
    initBB = cv2.selectROI('Selection', frame, showCrosshair=True)
    cv2.destroyWindow('Selection')
    # start OpenCV object tracker using the supplied bounding box
    if neuralTrack:
        [cx, cy, wi, hi] = get_axis_aligned_bbox(initBB)
        target_pos, target_sz = np.array([cx, cy]), np.array([wi, hi])
        state = SiamRPN_init(frame, target_pos, target_sz, net)
    else:
        tracker.init(frame, initBB)
    # thread2.start()
    tracking = True


# define the buttons and their commands
startButton = Button(root, text="Start Tracking", command=startTracking, activebackground='yellow')
plotButton = Button(root, text="Plot Graph", command=plotgraph, activebackground='yellow')
hFlipButton = Button(root, text="Flip HorizDir", command=swapHorizontal, activebackground='yellow')
vFlipButton = Button(root, text="Flip VertDir", command=swapVertical, activebackground='yellow')
screenButton = Button(root, text="Screenshot", command=screenshot, activebackground='yellow')
stopButton = Button(root, text="Quit", command=onClose, activebackground='yellow')
saveButton = Button(root, text="Save Plot", command=savePlot, activebackground='yellow')
homeButton = Button(root, text="Check Blur", command=calculateBlur, activebackground='yellow')
# buttons to control the movement
yposButton = Button(root, text="Y+", command=yPos, activebackground='yellow')
ynegButton = Button(root, text="Y-", command=yNeg, activebackground='yellow')
xposButton = Button(root, text="X+", command=xPos, activebackground='yellow')
xnegButton = Button(root, text="X-", command=xNeg, activebackground='yellow')
zposButton = Button(root, text="Z+", command=zPos, activebackground='yellow')
znegButton = Button(root, text="Z-", command=zNeg, activebackground='yellow')
stopmovButton = Button(root, text="S", command=stopMov, activebackground='yellow')

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

# place the buttons
startButton.grid(row=1, column=0, sticky='WENS')
plotButton.grid(row=1, column=1, sticky='WENS')
hFlipButton.grid(row=2, column=0, sticky='WENS')
vFlipButton.grid(row=2, column=1, sticky='WENS')
screenButton.grid(row=3, column=0, sticky='WENS')
stopButton.grid(row=3, column=1, sticky='WENS')
saveButton.grid(row=4, column=0, sticky='WENS')
homeButton.grid(row=4, column=1, sticky='WENS')
yposButton.grid(row=1, column=3, sticky='WENS')
ynegButton.grid(row=3, column=3, sticky='WENS')
xposButton.grid(row=2, column=4, sticky='WENS')
xnegButton.grid(row=2, column=2, sticky='WENS')
zposButton.grid(row=4, column=4, sticky='WENS')
znegButton.grid(row=4, column=2, sticky='WENS')
stopmovButton.grid(row=2, column=3, sticky='WENS')

# start videoloop thread
thread = threading.Thread(target=videoLoop, args=())
# thread2 = threading.Thread(target=threadedZAxis, args=())
thread.start()

root.wm_title("Trackoscope")

# kick off the GUI
root.mainloop()
