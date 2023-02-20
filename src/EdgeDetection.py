import cv2
import matplotlib.pyplot as plt
import numpy as np
import imutils
import pandas

# define source of video and blank arrays
vs = cv2.VideoCapture("./Video/ZOOMFASTTWO.mp4")
count = 0
frame_array = []
area_array = []


# find the number of contours
def grab_contours(cnts):
    # OpenCV v2.4, v4-official
    if len(cnts) == 2:
        return cnts[0]
    # OpenCV v3
    elif len(cnts) == 3:
        return cnts[1]


# loop through the frames of the video
while True:
    ret, frame = vs.read()

    count = count + 1

    # edge detection
    try:
        # resize video frame
        frame = imutils.resize(frame, width=700)
        # convert to grayscale image
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    except:
        break

    frame_array.append(count)

    # apply gaussian blur and extract edges
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    canny = cv2.Canny(blur, 10, 20)

    # show live preview
    ret, mask = cv2.threshold(canny, 250, 255, cv2.THRESH_BINARY)

    # create a binary thresholded image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
    mask = cv2.dilate(mask, kernel, iterations=1)
    cv2.imshow('Video feed', mask)

    # Close contour
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    close = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=3)

    # Find outer contour and fill with white
    cnts = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cv2.fillPoly(close, cnts, [255, 255, 255])

    area = 0
    for c in cnts:
        if cv2.contourArea(c) > 5000:
            area += cv2.contourArea(c)

    area_array.append(area)

    # show the image with the drawn contours
    cv2.imshow('contour', close)

    if cv2.waitKey(1) == 13:
        break

vs.release()

# plot stuff
plt.plot(frame_array, area_array, color='g')
plt.show()

cv2.destroyAllWindows()
