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
vertder = bool(True)
rotate = bool(False)
sendrepeat = bool(False)
centered = bool(False)
cameramode = bool(True)

# range limits
xrangehl = 65
xrangell = 35
yrangehl = 65
yrangell = 35

# open Arduino Serial
ser1 = serial.Serial('/dev/ttyACM0', 115200)
ser1.flush()
sleep(2)
portopen = True

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-t", "--tracker", type=str, default="csrt",
                help="OpenCV object tracker type")
args = vars(ap.parse_args())


# defines send command
def sendCommand(cmd):
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

# start video stream
print("[INFO] starting video stream...")
# if you want to run on laptop
# vs = VideoStream(src=0).start()
# if you want to run on Raspberry Pi
vs = PiVideoStream().start()
sleep(2.0)


# defines how to make a move depending on location of bounding box center
def makemove():
    global smallx, largex, centerx, smally, largey, centery, newxdirection, oldxdirection, newydirection, oldydirection, ydirection, xdirection, centered
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

    if (newydirection == 'Y') and (newxdirection == 'X'):
        centered = True
    else:
        centered = False

    return centered


# initialize the FPS throughput estimator
fps = FPS().start()

# loop over frames from the video stream
while True:
    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame
    if frame is None:
        break
    frame = imutils.resize(frame, width=500)
    (H, W) = frame.shape[:2]
    ovcenterx = W / 2
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
                              (255, 0, 0), 2)

    # update the FPS counter
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

    # show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 's' key is selected start tracking
    if key == ord("s"):
        initBB = cv2.selectROI("Frame", frame, fromCenter=False,
                               showCrosshair=True)
        # start OpenCV object tracker using the supplied bounding box
        tracker.init(frame, initBB)

    # if the 'q' key was pressed, break from the loop
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
