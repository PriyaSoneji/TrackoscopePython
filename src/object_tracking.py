# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import cv2
import serial
from time import sleep

# open Arduino Serial
ser1 = serial.Serial('COM3', 9600)
sleep(2)

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str,
                help="path to input video file")
ap.add_argument("-t", "--tracker", type=str, default="csrt",
                help="OpenCV object tracker type")
args = vars(ap.parse_args())

# define stuff for x-coordinate detection
ovcenterx = 0
smallx = 0
largex = 0
oldxdirection = 'N'
newxdirection = 'N'
centerx = 0

# define stuff for y-coordinate detection
ovcentery = 0
smally = 0
largey = 0
oldydirection = 'N'
newydirection = 'N'
centery = 0

# flipping variables
horizder = bool(False)
vertder = bool(False)
rotate = bool(False)
sendrepeat = bool(False)
centered = bool(False)

xrangeh = 55
xrangel = 45
yrangeh = 60
yrangel = 40


def sendCommand(cmd):
    ser1.write(cmd)
    s = ser1.readline();
    if not centered:
        ser1.write(cmd)
    # print("arduino sent back -> " + s.decode())

# extract the OpenCV version info
(major, minor) = cv2.__version__.split(".")[:2]

# if we are using OpenCV 3.2 OR BEFORE, we can use a special factory
# function to create our object tracker
if int(major) == 3 and int(minor) < 3:
    tracker = cv2.Tracker_create(args["tracker"].upper())

# otherwise, for OpenCV 3.3 OR NEWER, we need to explicity call the
# approrpiate object tracker constructor:
else:
    # initialize a dictionary that maps strings to their corresponding
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

    # grab the appropriate object tracker using our dictionary of
    # OpenCV object tracker objects
    tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()

# initialize the bounding box coordinates of the object we are going
# to track
initBB = None

# if a video path was not supplied, grab the reference to the web cam
if not args.get("video", False):
    print("[INFO] starting video stream...")
    vs = VideoStream(src=1).start()
    time.sleep(1.0)

# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])

# initialize the FPS throughput estimator
fps = None
print(xrangel, xrangeh, yrangel, yrangeh)
# loop over frames from the video stream
while True:
    # grab the current frame, then handle if we are using a
    # VideoStream or VideoCapture object
    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame

    # check to see if we have reached the end of the stream
    if frame is None:
        break

    # resize the frame (so we can process it faster) and grab the
    # frame dimensions
    frame = imutils.resize(frame, width=800)
    (H, W) = frame.shape[:2]
    ovcenterx = W/2

    # check to see if we are currently tracking an object
    if initBB is not None:
        # grab the new bounding box coordinates of the object
        (success, box) = tracker.update(frame)

        # check to see if the tracking was a success
        if success:
            (x, y, w, h) = [int(v) for v in box]
            smallx = x
            largex = x + w
            centerx = (smallx + largex)/2
            smally = y
            largey = y + h
            centery = (smally + largey)/2

            # Send X direction
            if ((centerx / W) * 100) > xrangeh:
                # print("out of bound - xh")
                if horizder:
                    newxdirection = 'L'
                else:
                    newxdirection = 'R'
            elif ((centerx / W) * 100) < xrangel:
                # print("out of bound - xl")
                if horizder:
                    newxdirection = 'R'
                else:
                    newxdirection = 'L'
            else:
                newxdirection = 'X'

            if (oldxdirection != newxdirection) or sendrepeat:
                sendCommand(newxdirection.encode())
                oldxdirection = newxdirection
                # print("Sent New X Direction")
                # print(oldxdirection)

            # Send Y direction
            if ((centery / H) * 100) > yrangeh:
                # print("out of bound - yh")
                if vertder:
                    newydirection = 'D'
                else:
                    newydirection = 'U'
            elif ((centery / H) * 100) < yrangel:
                # print("out of bound - yl")
                if vertder:
                    newydirection = 'U'
                else:
                    newydirection = 'D'
            else:
                newydirection = 'Y'

            if (oldydirection != newydirection) or sendrepeat:
                sendCommand(newydirection.encode())
                oldydirection = newydirection
                # print("Sent New Y Direction")
                # print(oldydirection)

            if (newydirection == 'Y') and (newxdirection == 'X'):
                centered = True
            else:
                centered = False

            cv2.rectangle(frame, (x, y), (x + w, y + h),
                          (0, 255, 0), 2)

        # update the FPS counter
        fps.update()
        fps.stop()

        # initialize the set of information we'll be displaying on
        # the frame
        info = [
            ("Success", "Yes" if success else "No"),
            ("FPS", "{:.2f}".format(fps.fps())),
            ("In Center", "Yes" if centered else "No"),
        ]

        # loop over the info tuples and draw them on our frame
        for (i, (k, v)) in enumerate(info):
            text = "{}: {}".format(k, v)
            cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # print(key)

    # stop if space bar
    if key == ord("5"):
        sendCommand('S'.encode())
    if key == ord("8"):
        if vertder:
            sendCommand('U'.encode())
        else:
            sendCommand('D'.encode())
    if key == ord("2"):
        if vertder:
            sendCommand('D'.encode())
        else:
            sendCommand('U'.encode())
    if key == ord("4"):
        if vertder:
            sendCommand('L'.encode())
        else:
            sendCommand('R'.encode())
    if key == ord("6"):
        if vertder:
            sendCommand('R'.encode())
        else:
            sendCommand('L'.encode())

    # if the 's' key is selected, we are going to "select" a bounding
    # box to track
    if key == ord("s"):
        # select the bounding box of the object we want to track (make
        # sure you press ENTER or SPACE after selecting the ROI)
        initBB = cv2.selectROI("Frame", frame, fromCenter=False,
                               showCrosshair=True)

        # start OpenCV object tracker using the supplied bounding box
        # coordinates, then start the FPS throughput estimator as well
        tracker.init(frame, initBB)
        fps = FPS().start()

    # if the 'h' key was pressed, the horizontal direction is flipped
    if key == ord("h"):
        horizder = not horizder
        print("flipped horizontal")

    if key == ord("v"):
        vertder = not vertder
        print("flipped vertical")

    # if the `q` key was pressed, break from the loop
    elif key == ord("q"):
        sendCommand('S'.encode())
        break

# if we are using a webcam, release the pointer
sendCommand('S'.encode())
if not args.get("video", False):
    vs.stop()

# otherwise, release the file pointer
else:
    vs.release()

# close all windows
cv2.destroyAllWindows()
