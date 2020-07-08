# import the necessary packages
from imutils.video import FPS
import argparse
import imutils
import threading
import time
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
    global portopen, ser1
    if portopen:
        thread2 = threading.Thread(target=sendCommandThread, args=(cmd, ser1))
        thread2.start()


# sends command to the Arduino over serial port
def sendCommandThread(cmd, serport):
    serport.write(cmd)
    if not centered:
        serport.write(cmd)


# start video stream
print("[INFO] starting video stream...")
vs = PiVideoStream().start()
sleep(2.0)

# initialize the FPS throughput estimator
fps = None


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
        fps = FPS().start()

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
