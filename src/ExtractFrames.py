import cv2
import math
import numpy as np

# Capture every n seconds (here, n = 5)

#################### Setting up the file ################
videoFile = "AmoebaCrawl.mp4"
vidcap = cv2.VideoCapture(videoFile)
success, image = vidcap.read()

#################### Setting up parameters ################

seconds = 1
fps = vidcap.get(cv2.CAP_PROP_FPS)  # Gets the frames per second
multiplier = fps * seconds

#################### Initiate Process ################
count = 0

while success:
    frameId = int(round(vidcap.get(
        1)))  # current frame number, rounded b/c sometimes you get frame intervals which aren't integers...this adds a little imprecision but is likely good enough
    success, image = vidcap.read()

    if frameId % multiplier == 0:
        cv2.imwrite("Frames/crawl%d.jpg" % count, image)
        count = count + 1

vidcap.release()
print("Complete")
