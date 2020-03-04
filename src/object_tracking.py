# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import cv2
import sys
import glob
import serial
from time import sleep

# define stuff for x-coordinate detectionx
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

# range limits
xrangehl = 55
xrangell = 45
yrangehl = 55
yrangell = 45
xrangehs = 65
xrangels = 35
yrangehs = 65
yrangels = 35
availvid = []


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

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str,
                help="path to input video file")
ap.add_argument("-t", "--tracker", type=str, default="csrt",
                help="OpenCV object tracker type")
args = vars(ap.parse_args())


# sends command to the Arduino over serial port
def sendCommand(cmd):
    if portopen:
        ser1.write(cmd)
        if not centered:
            ser1.write(cmd)


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


# Checks for a valid camera
def testDevice(source):
    print("Trying video source", source)
    cap = cv2.VideoCapture(source)
    if cap is None or not cap.isOpened():
        return False
    else:
        return True


# if a video path was not supplied, grab the reference to the web cam
if not args.get("video", False):
    print("[INFO] starting video stream...")
    for x in range(3):
        if testDevice(x):
            availvid.append(x)
    vs = VideoStream(src=(availvid[len(availvid) - 1])).start()
    time.sleep(1.0)

# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])

# initialize the FPS throughput estimator
fps = None


# defines how to make a move depending on location of bounding box center
def makemove():
    global smallx, largex, centerx, smally, largey, centery, newxdirection, oldxdirection, newydirection, oldydirection, ydirection, xdirection
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
            else:
                newxdirection = 'R'
        elif ((centerx / W) * 100) < xrangell:
            if horizder:
                newxdirection = 'R'
            else:
                newxdirection = 'L'
        else:
            newxdirection = 'X'
        if (oldxdirection != newxdirection) or sendrepeat:
            sendCommand(newxdirection.encode())
            oldxdirection = newxdirection
        # Send Y direction
        if ((centery / H) * 100) > yrangehl:
            if vertder:
                newydirection = 'D'
            else:
                newydirection = 'U'
        elif ((centery / H) * 100) < yrangell:
            if vertder:
                newydirection = 'U'
            else:
                newydirection = 'D'
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
            else:
                xdirection = 'r'
        elif ((centerx / W) * 100) < xrangels:
            if horizder:
                xdirection = 'r'
            else:
                xdirection = 'l'
        else:
            xdirection = 'x'
        if (xdirection != 'x') or sendrepeat:
            sendCommand(xdirection.encode())
        # Send Y direction
        if ((centery / H) * 100) > yrangehs:
            if vertder:
                ydirection = 'd'
            else:
                ydirection = 'u'
        elif ((centery / H) * 100) < yrangels:
            if vertder:
                ydirection = 'u'
            else:
                ydirection = 'd'
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
    if key == ord("5"):
        print("manual stop")
        sendCommand('S'.encode())
        print("sent")
        # sendCommand('s'.encode())
    if key == ord("8"):
        print("Up/Down")
        if vertder:
            sendCommand('u'.encode())
        else:
            sendCommand('d'.encode())
    if key == ord("2"):
        print("Up/Down")
        if vertder:
            sendCommand('d'.encode())
        else:
            sendCommand('u'.encode())
    if key == ord("4"):
        print("Left/Right")
        if horizder:
            sendCommand('r'.encode())
        else:
            sendCommand('l'.encode())
    if key == ord("6"):
        print("Left/Right")
        if horizder:
            sendCommand('l'.encode())
        else:
            sendCommand('r'.encode())


# loop over frames from the video stream
while True:
    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame
    if frame is None:
        break
    frame = imutils.resize(frame, width=800)
    (H, W) = frame.shape[:2]
    ovcenterx = W / 2
    # check to see if we are currently tracking an object
    if initBB is not None:
        # grab the new bounding box coordinates of the object
        (success, box) = tracker.update(frame)
        if success:
            (x, y, w, h) = [int(v) for v in box]
            centered = makemove()
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                          (0, 255, 0), 2)
        # update the FPS counter
        fps.update()
        fps.stop()

        # initialize info on screen
        info = [
            ("Tracking Success", "Yes" if success else "No"),
            ("X-Move", oldxdirection),
            ("Y-Move", oldydirection),
            ("In Center", "Yes" if centered else "No"),
        ]
        for (i, (k, v)) in enumerate(info):
            text = "{}: {}".format(k, v)
            cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    # show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    manualmove()

    # if the 's' key is selected start tracking
    if key == ord("s"):
        initBB = cv2.selectROI("Frame", frame, fromCenter=False,
                               showCrosshair=True)
        # start OpenCV object tracker using the supplied bounding box
        tracker.init(frame, initBB)
        fps = FPS().start()

    # if the 'h' key was pressed, the horizontal direction is flipped
    if key == ord("h"):
        horizder = not horizder
        print("flipped horizontal")

    if key == ord("v"):
        vertder = not vertder
        print("flipped vertical")

    if key == ord("m"):
        cameramode = not cameramode
        print("mode has been changed")

    # if the `q` key was pressed, break from the loop
    elif key == ord("q"):
        sendCommand('S'.encode())
        break

# if we are using a webcam, release the pointer
sendCommand('S'.encode())
if not args.get("video", False):
    vs.stop()
else:
    vs.release()

# close all windows
cv2.destroyAllWindows()
