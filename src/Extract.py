import cv2
from time import sleep
import matplotlib.pyplot as plt
import numpy as np
import imutils
import pandas

# define source of video and blank arrays
cap = cv2.VideoCapture("./Video/ZOOMFASTTWO.mp4")

count = 0

while cap.isOpened():
    ret, frame = cap.read()

    if ret:
        name = 'Image_' + str(count)
        cv2.imwrite('./Video/Images/frameswim{:d}.jpg'.format(count), frame)
        count += 30  # i.e. at 30 fps, this advances one second
        cap.set(cv2.CAP_PROP_POS_FRAMES, count)
    else:
        cap.release()
        break
