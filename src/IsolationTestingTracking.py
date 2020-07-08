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

# flipping variables
portopen = bool(False)

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
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                          (0, 255, 0), 2)

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

    # if the 's' key is selected start tracking
    if key == ord("s"):
        initBB = cv2.selectROI("Frame", frame, fromCenter=False,
                               showCrosshair=True)
        # start OpenCV object tracker using the supplied bounding box
        tracker.init(frame, initBB)

# if we are using a webcam, release the pointer
sendCommand('S'.encode())

if not args.get("video", False):
    vs.stop()
else:
    vs.release()

# close all windows
cv2.destroyAllWindows()
