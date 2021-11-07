# make sure bluetooth is off
import threading
import cv2
from time import sleep
import glob
from imutils.video import VideoStream
from src_new.arduino_communication import *
from src_new.basic_tracking import *
from src_new.trajectory_mapping import *
from src_new.gui import *
from src_new.zaxis import *

vs = None


# Checks for a valid camera
def testDevice(source):
    cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
    if cap is None or not cap.isOpened():
        return False
    else:
        return True


def initialize_all():
    open_comm()

    print("[INFO] starting video stream...")
    # for x in range(3):
    #     if testDevice(x):
    #         availvid.append(x)

    # vs = VideoStream(src=(availvid[-1])).start()
    vs = VideoStream(src=1).start()
    sleep(1.0)

    button_init()
    def_fig1()


def onClose():
    global root, stopEvent
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
