import cv2
import matplotlib.pyplot as plt
import numpy as np
import imutils
import pandas

# define source of video and blank arrays
vs = cv2.VideoCapture("./Video/Stentor_Trim.mp4")
count = 0
edge_array = []
laplacian_array = []
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
    # apply gaussian blur and extract edges
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    canny = cv2.Canny(blur, 10, 35)

    # apply morphology close
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    morph = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel)

    # get contours and keep largest
    contours = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    big_contour = max(contours, key=cv2.contourArea)

    cnts = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = grab_contours(cnts)

    contour_image = canny.copy()
    area = 0

    for c in cnts:
        if cv2.contourArea(c) > 5000:
            area += cv2.contourArea(c)
            contour_image = cv2.drawContours(contour_image, [c], 0, (100, 5, 10), 3)

    # cv2.imshow('Video feed2', contour_image)

    area_array.append(area)

    # get number of vertices (sides)
    peri = cv2.arcLength(big_contour, True)
    approx = cv2.approxPolyDP(big_contour, 0.01 * peri, True)

    frame_array.append(count)
    edge_array.append(len(approx))

    # show live preview
    ret, mask = cv2.threshold(canny, 250, 255, cv2.THRESH_BINARY)
    cv2.imshow('Video feed', mask)

    # create a binary thresholded image
    _, binary = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY_INV)

    # find the contours from the thresholded image
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # draw all contours
    image = cv2.drawContours(binary, contours, -1, (0, 255, 0), 2)
    # show the image with the drawn contours
    cv2.imshow('contour', image)

    if cv2.waitKey(1) == 13:
        break

vs.release()
print(frame_array)
print(edge_array)
print(len(edge_array))
# array for speed of track taken from grapher.py
speed_array = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 54, 18, 18, 11, 11, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 38, 38, 49,
               49, 39, 41, 49, 8, 8, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 49, 49, 54, 54, 54, 49, 44, 44, 38, 38, 44,
               44, 44, 38, 38, 38, 38, 44, 44, 44, 44, 39, 39, 38, 38, 38, 38, 44, 44, 44, 44, 39, 39, 54, 39, 39, 39,
               39, 41, 41, 38, 39, 39, 39, 39, 39, 49, 38, 38, 38, 39, 39, 11, 38, 3, 54, 54, 54, 54, 4, 4, 54, 54, 54,
               54, 54, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 39, 39, 39, 39, 54, 54, 54, 54, 54, 54,
               54, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 54, 54, 54, 54, 39, 39, 39, 39, 39, 39, 54,
               54, 39, 39, 39, 38, 38, 38, 38, 49, 49, 49, 54, 54, 54, 49, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 18, 18, 3, 1, 2, 54, 54, 54, 54, 38, 38, 38, 38, 54, 54, 54, 54, 54, 38, 38, 38,
               38, 38, 38, 38, 38, 38, 41, 41, 54, 54, 54, 54, 54, 54, 54, 54, 49, 49, 49, 49, 49, 49, 49, 49, 49, 49,
               49, 49, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 49,
               49, 49, 41, 54, 54, 54, 54, 54, 7, 7, 7, 7, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 3, 38, 38, 38, 38,
               38, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 38, 38, 38, 38, 38, 38, 38, 38, 38, 54, 11, 54, 54, 54,
               27, 54, 54, 54, 44, 44, 54, 54, 54, 49, 49, 49, 49, 49, 38, 38, 38, 54, 54, 54, 54, 54, 54, 54, 54, 54,
               54, 54, 54, 54, 54, 41, 44, 44, 44, 41, 41, 41, 41, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38,
               38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 54, 18, 18, 54, 54, 54, 54,
               54, 3, 3, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 11, 38, 38, 54, 41, 49, 49,
               49, 10, 10, 10, 10, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 54, 54, 54, 54, 54, 54, 54, 54, 54,
               44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 8, 54, 44, 54, 54, 41, 41, 49, 49, 38, 38, 44,
               44, 54, 54, 54, 54, 24, 39, 39, 39, 39, 39, 39, 39, 39, 54, 54, 54, 38, 38, 38, 54, 39, 0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 4, 19, 19, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38,
               38, 38, 38, 22, 54, 5, 38, 38, 38, 38, 38, 13, 2, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 54, 13, 13,
               13, 13, 13, 38, 38, 38, 38, 4, 19, 27, 54, 54, 54, 54, 54, 54, 27, 54, 54, 54, 39, 39, 39, 39, 41, 41,
               49, 41, 15, 15, 54, 54, 54, 13, 27, 54, 54, 12, 54, 19, 19, 38, 38, 38, 38, 54, 54, 54, 54, 54, 38, 38,
               38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 38, 38, 38, 38, 38,
               41, 41, 41, 54, 54, 54, 54, 10, 54, 54, 38, 38, 38, 38, 38, 44, 44, 44, 27, 41, 41, 54, 5, 14, 18, 14,
               14, 54, 54, 54, 54, 27, 6, 41, 27, 27, 11, 39, 39, 39, 39, 39, 38, 38, 38, 38, 27, 15, 15, 38, 38, 38,
               38, 38, 38, 38, 38, 38, 54, 54, 54, 39, 39, 39, 39, 38, 38, 38, 38, 38, 38, 38, 38, 54, 54, 54, 54, 54,
               54, 54, 8, 8, 27, 54, 54, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 54, 54, 54, 54, 11, 10, 10, 3, 8, 11, 2, 38, 38, 54, 54, 54, 41, 41, 8, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 54,
               54, 54, 54, 54, 44, 54, 54, 39, 39, 39, 54, 54, 39, 6, 13, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54,
               54, 54, 44, 44, 44, 3, 3, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 41, 41, 41, 41, 41, 41, 41, 41, 41,
               41, 44, 44, 44, 44, 41, 39, 39, 39, 39, 39, 39, 24, 38, 38, 38, 41, 18, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 54, 54, 54, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 13, 4, 2, 2, 38,
               38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38]

# plot stuff
np.savetxt('./CSVFiles/Stentor_Crop.csv', edge_array, delimiter=',')
plt.plot(frame_array, edge_array, color='b')
plt.plot(frame_array, speed_array, color='r')
plt.plot(frame_array, area_array, color='g')

# save the output into csv
df = pandas.DataFrame(data={"frame": frame_array, "edges": edge_array, "speed": speed_array})
df.to_csv("./Video/edgevsspeed.csv", sep=',', index=False)

# plt.plot(frame_array, laplacian_array, color='r')
plt.show()

cv2.destroyAllWindows()
