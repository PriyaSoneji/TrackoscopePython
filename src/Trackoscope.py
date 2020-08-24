# make sure bluetooth is off
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
from serial import Serial
import pyautogui
import glob
import numpy as np
from imutils.video import VideoStream
from imutils.video import FPS
from pandas import DataFrame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
rotate = bool(False)
sendrepeat = bool(False)
centered = bool(False)
tracking = bool(False)

# range limits
xrangehl = 60
xrangell = 40
yrangehl = 60
yrangell = 40

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
blurcap = 40

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


def fft_blur_detection(image, thresh):
    (h, w) = image.shape
    (cX, cY) = (int(w / 2.0), int(h / 2.0))

    fft = np.fft.fft2(image)
    fftShift = np.fft.fftshift(fft)

    fftShift[cY - 60:cY + 60, cX - 60:cX + 60] = 0
    fftShift = np.fft.ifftshift(fftShift)
    recon = np.fft.ifft2(fftShift)

    magnitude = 20 * np.log(np.abs(recon))
    mean = np.mean(magnitude)

    return mean, mean <= thresh


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
    # ser1 = serial.Serial(availableport[0], 2000000)
    ser1 = serial.Serial("COM3", 2000000)
    sleep(1)
    ser1.flush()
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


def sendCommand(cmd):
    global portopen, ser1, centered
    if portopen:
        ser1.write(cmd)


def sendCommandT(cmd):
    global portopen, ser1
    if portopen:
        thread3 = threading.Thread(target=sendCommandThread, args=(cmd, ser1))
        thread3.start()


# sends command to the Arduino over serial port
def sendCommandThread(cmd, serport):
    serport.write(cmd)
    print("sent command")


fps = FPS().start()


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
    sendCommand('E'.encode())
    vs.stop()
    initBB = None
    stopEvent.set()
    root.quit()
    sys.exit()


sendIter = 0


# defines how to make a move depending on location of bounding box center
def makemove():
    global smallx, largex, centerx, smally, largey, centery, newxdirection, oldxdirection, newydirection, \
        oldydirection, ydirection, xdirection, x, y, w, h, W, H, currx, curry, centered, sendIter
    smallx = x
    largex = x + w
    centerx = (smallx + largex) / 2
    smally = y
    largey = y + h
    centery = (smally + largey) / 2

    # Send X direction
    if ((centerx / W) * 100) > xrangehl:
        newxdirection = 'R'
        currx = currx - 1
        addpoint()
    elif ((centerx / W) * 100) < xrangell:
        newxdirection = 'L'
        currx = currx + 1
        addpoint()
    else:
        newxdirection = 'X'

    if oldxdirection != newxdirection:
        sendCommand(newxdirection.encode())
        oldxdirection = newxdirection

    if sendIter == 50:
        sendCommand(oldxdirection.encode())

    # Send Y direction
    if ((centery / H) * 100) > yrangehl:
        newydirection = 'U'
        curry = curry - 1
        addpoint()
    elif ((centery / H) * 100) < yrangell:
        newydirection = 'D'
        curry = curry + 1
        addpoint()

    else:
        newydirection = 'Y'
    if oldydirection != newydirection:
        sendCommand(newydirection.encode())
        oldydirection = newydirection

    if sendIter == 50:
        sendCommand(oldydirection.encode())
        sendIter = 0

    if (newydirection == 'Y') and (newxdirection == 'X'):
        centered = True
        sendIter = 0
    else:
        centered = False
        sendIter = sendIter + 1

    return centered


# figure one data
figure1 = plt.Figure(figsize=(6, 5), dpi=100)
ax = figure1.add_subplot(111, projection='3d')
bar1 = FigureCanvasTkAgg(figure1, root)
bar1.get_tk_widget().grid(row=0, column=1)


def focusing():
    global blurry
    calculateBlur()
    if blurry:
        fixBlurMotor()


def threadedZAxis():
    while not stopEvent.is_set():
        # Z-Axis Detection
        focusing()
        sleep(2)


# calculates the blur and returns the blur number
def calculateBlur():
    global focus, blurry, blurcap
    image = vs.read()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    focus = round(variance_of_laplacian(gray), 2)
    if focus < blurcap:
        blurry = bool(False)
    else:
        blurry = bool(True)

    # (focus, blurry) = fft_blur_detection(gray, blurcap)
    print("Focus: " + str(focus))
    return focus


# uses a motor to fix the blur
def fixBlurMotor():
    global originalFocus, compareFocus, rightDirection, focus, zdirection, blurcap
    originalFocus = calculateBlur()
    zdirection = 'b'
    sendCommand(zdirection.encode())
    sleep(1)

    compareFocus = calculateBlur()
    print("Compare Focus: " + str(compareFocus))

    if compareFocus < originalFocus:
        rightDirection = bool(True)
    else:
        rightDirection = bool(False)

    if rightDirection:
        print("went in if")
        for j in range(10):
            zdirection = 'b'
            sendCommand(zdirection.encode())
            sleep(1)
            if calculateBlur() < blurcap:
                print("focused now")
                break
    else:
        print("went in else")
        for k in range(10):
            zdirection = 't'
            sendCommand(zdirection.encode())
            sleep(1)
            if calculateBlur() < blurcap:
                print("focused now")
                break

    calculateBlur()
    zdirection = 'Z'
    sendCommand(zdirection.encode())
    print("end focusing")


def yPos():
    sendCommand('U'.encode())


def yNeg():
    sendCommand('D'.encode())


def xPos():
    sendCommand('R'.encode())


def xNeg():
    sendCommand('L'.encode())


def zPos():
    sendCommand('t'.encode())


def zNeg():
    sendCommand('b'.encode())


def stopMov():
    sendCommand('S'.encode())


def hardStop():
    sendCommand('E'.encode())
    ser1.flush()


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
    global frame, initBB, tracker, tracking, thread2, ser1
    # if the 's' key is selected start tracking
    initBB = cv2.selectROI('Selection', frame, showCrosshair=True)
    cv2.destroyWindow('Selection')
    # start OpenCV object tracker using the supplied bounding box
    tracker.init(frame, initBB)
    ser1.flush()
    # thread2.start()
    tracking = True


# define the buttons and their commands
startButton = Button(root, text="Start Tracking", command=startTracking, activebackground='yellow')
plotButton = Button(root, text="Plot Graph", command=plotgraph, activebackground='yellow')
zFocusButton = Button(root, text="Focus", command=focusing, activebackground='yellow')
hardStopButton = Button(root, text="Hard Stop", command=hardStop, activebackground='yellow')
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
    # vs = VideoStream(src=0).start()
    sleep(1.0)
# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])

# place the buttons
startButton.grid(row=1, column=0, sticky='WENS')
plotButton.grid(row=1, column=1, sticky='WENS')
zFocusButton.grid(row=2, column=0, sticky='WENS')
hardStopButton.grid(row=2, column=1, sticky='WENS')
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
thread2 = threading.Thread(target=threadedZAxis, args=())
thread.start()

root.wm_title("Trackoscope")

# kick off the GUI
root.mainloop()
