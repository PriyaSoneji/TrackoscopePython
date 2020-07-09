import tkinter as tk
from tkinter import *
from PIL import Image
from PIL import ImageTk
import imutils
import threading
import argparse
import cv2
from time import sleep
from imutils.video import VideoStream
from imutils.video import FPS
from pandas import DataFrame
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

x_values = []
y_values = []
z_values = []

x_values.append(0)
y_values.append(0)
z_values.append(0)


# initialize the window toolkit along with the two image panels
root = Tk()
panelA = None
panelB = None
frame = None
thread = None
stopEvent = threading.Event()


fps = FPS().start()


# main video loop that sets everything and refreshes the screen
def videoLoop():
    global vs, panelB, frame, fps
    try:
        # keep looping over frames until we are instructed to stop
        while not stopEvent.is_set():
            # grab the frame from the video stream and resize it to
            # have a maximum width of 300 pixels
            frame = vs.read()
            frame = imutils.resize(frame, width=500)
            (H, W) = frame.shape[:2]

            fps.update()
            fps.stop()

            # initialize info on screen
            info = [
                ("FPS", "{:.2f}".format(fps.fps()))
            ]

            for (i, (k, v)) in enumerate(info):
                text = "{}: {}".format(k, v)
                cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

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


# figure one data
figure1 = plt.Figure(figsize=(5, 4), dpi=100)
ax = figure1.add_subplot(111, projection='3d')
bar1 = FigureCanvasTkAgg(figure1, root)
bar1.get_tk_widget().grid(row=0, column=1)


# plots the graph using matplotlib
def plotgraph():
    # grab a reference to the image panels
    global panelA, figure1, ax, root, z_values

    # plot
    ax.plot(x_values, y_values, z_values)
    ax.scatter(x_values, y_values, z_values)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # idle draw
    bar1.draw_idle()


# start video stream
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
sleep(1.0)


# start videoloop thread
thread = threading.Thread(target=videoLoop, args=())
thread.start()

root.wm_title("Trackoscope")

# kick off the GUI
root.mainloop()
