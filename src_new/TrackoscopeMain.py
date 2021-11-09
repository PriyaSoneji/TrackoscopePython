# make sure bluetooth is off
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


# open_comm()
availvid = []

print("[INFO] starting video stream...")
for x in range(3):
    if testDevice(x):
        availvid.append(x)

vs = VideoStream(src=(availvid[-1])).start()
# vs = VideoStream(src=1).start()
sleep(1.0)

button_init()
def_fig1()

# start videoloop thread
thread = threading.Thread(target=videoLoop, args=(vs))
thread2 = threading.Thread(target=threadedZAxis, args=())
thread.start()

root.wm_title("Trackoscope")

# kick off the GUI
root.mainloop()
