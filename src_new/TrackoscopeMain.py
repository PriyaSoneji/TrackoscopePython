# make sure bluetooth is off
from src_new.arduino_communication import *
from src_new.basic_tracking import *
from src_new.trajectory_mapping import *
from src_new.initialization import *
from src_new.gui import *
from src_new.zaxis import *

initialize_all()

# start videoloop thread
thread = threading.Thread(target=videoLoop, args=())
thread2 = threading.Thread(target=threadedZAxis, args=())
thread.start()

root.wm_title("Trackoscope")

# kick off the GUI
root.mainloop()
