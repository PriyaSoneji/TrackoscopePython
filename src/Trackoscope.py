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
import pandas
import glob
import numpy as np
from imutils.video import VideoStream
from imutils.video import FPS
from pandas import DataFrame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import csv

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
trackingsuccess = bool(False)
showOverlay = bool(True)
speedMode = bool(True)

# range limits
xrangehl = 60
xrangell = 40
yrangehl = 60
yrangell = 40

# graphing stuff
currx = 0
curry = 0

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
timestamps = []

x_values.append(0)
y_values.append(0)
z_values.append(0)

now = datetime.datetime.now()
timestamp = str(now.strftime("%H:%M:%S"))
timestamps.append(timestamp)

availvid = []

trackinginZ = bool(False)


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
    figure1.savefig('graph.png')


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

count = 0
countmax = 10
countgraph = 0
countgraphmax = 30


# add points to the graph and updates plot
def addpoint():
    global count, countmax, figure1, zval, countgraph, countgraphmax, timestamps
    if count == countmax:
        x_values.append(round(currx, 2))
        y_values.append(round(curry, 2))
        z_values.append(round(zval, 2))
        now = datetime.datetime.now()
        timestamp = str(now.strftime("%H:%M:%S"))
        timestamps.append(timestamp)
        count = 0
    if countgraph == countgraphmax:
        plotgraph()
        countgraph = 0
    count = count + 1
    countgraph = countgraph + 1


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

# function to create our object tracker

tracker = cv2.TrackerCSRT_create()

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
infovar = StringVar()


def videoLoop():
    global vs, panelB, frame, initBB, x, y, w, h, H, W, centered, fps, trackingsuccess, centerx, centery, showOverlay, oldxdirection, oldydirection
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


# the micrometers per send
basestepsize = 86.24
incrementstepxy = basestepsize/16


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


# figure one data
figure1 = plt.Figure(figsize=(6, 5), dpi=100)
if trackinginZ:
    ax = figure1.add_subplot(111, projection='3d')
else:
    ax = figure1.add_subplot(111)
bar1 = FigureCanvasTkAgg(figure1, root)
bar1.get_tk_widget().grid(row=0, column=1)

blurcap = 24
ogfocus = 0


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
    global focus, blurry, blurcap, tracking, x, y, w, h
    if tracking:
        image = vs.read()
        image = image[y:y + h, x:x + w]
    else:
        image = vs.read()

    image = vs.read()

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    focus = round(variance_of_laplacian(gray), 2)
    # focus = round(cv2.Laplacian(image, cv2.CV_64F).var(), 2)
    if focus > blurcap:
        blurry = bool(False)
    else:
        blurry = bool(True)

    # (focus, blurry) = fft_blur_detection(gray, blurcap)
    # focus = round(focus, 2)

    setFocusLabel()
    return focus


updowncount = 0
zval = 0


# uses a motor to fix the blur
def fixBlurMotor():
    global originalFocus, compareFocus, rightDirection, focus, zdirection, blurcap, ogfocus, updowncount, zval, incrementstepxy
    rightDirection = bool(True)
    zdirection = 'b'
    ogfocus = focus
    originalFocus = focus
    updowncount = zval
    for j in range(20):
        sleep(0.50)
        compareFocus = calculateBlur()

        if abs(compareFocus - originalFocus) > 0.5:
            if compareFocus > originalFocus:
                rightDirection = bool(True)
            else:
                rightDirection = bool(False)
            originalFocus = focus
        elif ((blurcap - compareFocus) - (blurcap - ogfocus)) > 1:
            # print("too far")
            rightDirection = bool(False)

        if not blurry:
            print("focused now")
            zdirection = 'S'
            sendCommand(zdirection.encode())
            break

        if not rightDirection:
            # print("Change")
            if zdirection == 't':
                zdirection = 'b'
            else:
                zdirection = 't'

        if zdirection == 't':
            updowncount = updowncount + incrementstepxy
        else:
            updowncount = updowncount - incrementstepxy

        sendCommand(zdirection.encode())

    zval = updowncount
    addpoint()
    print("ended")


def setFocusLabel():
    global focus, infovar
    infovar.set("Focus: " + str(focus))


def yPos():
    sendCommand('D'.encode())


def yNeg():
    sendCommand('U'.encode())


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


def changeOveraly():
    global showOverlay
    showOverlay = not showOverlay
    if showOverlay:
        infovar.set("Showing Tracker")
    else:
        infovar.set("Just Showing Video")


def changeSpeedMode():
    global speedMode
    speedMode = not speedMode
    if speedMode:
        infovar.set("Set to Optimal Speed")
    else:
        infovar.set("Now Full Stop in Between")


def dataSave():
    global z_values, y_values, x_values, trackinginZ, timestamps
    if trackinginZ:
        df = pandas.DataFrame(data={"xval": x_values, "yval": y_values, "zval": z_values, "times": timestamps})
        df.to_csv("./trackingvals.csv", sep=',', index=False)
    else:
        df = pandas.DataFrame(data={"xval": x_values, "yval": y_values, "times": timestamps})
        df.to_csv("./trackingvals.csv", sep=',', index=False)


# plots the graph using matplotlib
def plotgraph():
    # grab a reference to the image panels
    global panelA, figure1, ax, root, x_values, y_values, z_values, trackinginZ

    ax.cla()

    # plot
    if trackinginZ:
        ax.plot(x_values, y_values, z_values, color='black', linestyle='solid', marker='+',
                markerfacecolor='blue', markevery=[-1])
        ax.set_xlabel('X-Movement (μm)')
        ax.set_ylabel('Y-Movement (μm)')
        ax.set_zlabel('Z-Movement (μm)')
    else:
        ax.plot(x_values, y_values, color='green', linestyle='solid', marker='H',
                markerfacecolor='blue', markersize=8, markevery=[-1])
        ax.set_xlabel('X-Movement (μm)')
        ax.set_ylabel('Y-Movement (μm)')

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


# define the buttons and their commands
startButton = Button(root, text="Start Tracking", command=startTracking, activebackground='yellow')
plotButton = Button(root, text="Plot Graph", command=plotgraph, activebackground='yellow')
zFocusButton = Button(root, text="Focus", command=focusing, activebackground='yellow')
speedButton = Button(root, text="Change Speed Mode", command=changeSpeedMode, activebackground='yellow')
dataButton = Button(root, text="Save Data", command=dataSave, activebackground='yellow')
hideButton = Button(root, text="Change Overlay", command=changeOveraly, activebackground='yellow')
blurButton = Button(root, text="Check Blur", command=calculateBlur, activebackground='yellow')
infoLabel = Label(root, textvariable=infovar, font=("Times", 16))
# buttons to control the movement
yposButton = Button(root, text="Y+", command=yPos, activebackground='yellow')
ynegButton = Button(root, text="Y-", command=yNeg, activebackground='yellow')
xposButton = Button(root, text="X+", command=xPos, activebackground='yellow')
xnegButton = Button(root, text="X-", command=xNeg, activebackground='yellow')
zposButton = Button(root, text="Z+", command=zPos, activebackground='yellow')
znegButton = Button(root, text="Z-", command=zNeg, activebackground='yellow')
stopmovButton = Button(root, text="S", command=stopMov, activebackground='yellow')

# if a video path was not supplied, grab the reference to the web cam

print("[INFO] starting video stream...")
for x in range(3):
    if testDevice(x):
        availvid.append(x)
vs = VideoStream(src=(availvid[len(availvid) - 1])).start()
# vs = VideoStream(src=0).start()
sleep(1.0)

# place the buttons
startButton.grid(row=1, column=0, sticky='WENS')
plotButton.grid(row=1, column=1, sticky='WENS')
zFocusButton.grid(row=2, column=0, sticky='WENS')
speedButton.grid(row=2, column=1, sticky='WENS')
dataButton.grid(row=3, column=0, sticky='WENS')
hideButton.grid(row=3, column=1, sticky='WENS')
blurButton.grid(row=4, column=1, sticky='WENS')
yposButton.grid(row=1, column=3, sticky='WENS')
ynegButton.grid(row=3, column=3, sticky='WENS')
xposButton.grid(row=2, column=4, sticky='WENS')
xnegButton.grid(row=2, column=2, sticky='WENS')
zposButton.grid(row=4, column=4, sticky='WENS')
znegButton.grid(row=4, column=2, sticky='WENS')
stopmovButton.grid(row=2, column=3, sticky='WENS')
infoLabel.grid(row=4, column=0, sticky='WENS')

# start videoloop thread
thread = threading.Thread(target=videoLoop, args=())
thread2 = threading.Thread(target=threadedZAxis, args=())
thread.start()

root.wm_title("Trackoscope")

# kick off the GUI
root.mainloop()
