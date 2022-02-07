import cv2
import matplotlib.pyplot as plt
import numpy as np
import imutils
import pandas

# define source of video and blank arrays
vs = cv2.VideoCapture("./Video/Stentor_Stop_Go_Raw_Cropped.mp4")
count = 0
video = cv2.VideoWriter('mygeneratedvideo.avi', 0, 1, (700, 385))
frame_array = []
area_array = []

# loop through the frames of the video
while True:
    ret, frame = vs.read()

    count = count + 1
    num_white = 0

    # edge detection
    try:
        # resize video frame
        frame = imutils.resize(frame, width=700)
    except:
        break

    dimensions = frame.shape
    h = dimensions[0]
    w = dimensions[1]

    r = np.zeros((h, w), dtype="uint8")
    g = np.zeros((h, w), dtype="uint8")
    b = np.zeros((h, w), dtype="uint8")

    for i in range(h):
        for j in range(w):
            (l, m, n) = frame[i, j]
            if n > 60 or n < 35:
                r[i, j] = 0
                g[i, j] = 0
                b[i, j] = 0
            else:
                if l > 90:
                    r[i, j] = 0
                    g[i, j] = 0
                    b[i, j] = 0
                else:
                    # print(l, m, n)
                    num_white = num_white + 1
                    r[i, j] = 255
                    g[i, j] = 255
                    b[i, j] = 255

    area_array.append(num_white / 900)
    frame_array.append(count)
    num_white = 0

    r = r.astype("uint8")
    g = g.astype("uint8")
    b = b.astype("uint8")

    mask = cv2.merge((b, g, r))

    # show live preview
    cv2.imshow('Video feed', mask)
    video.write(mask)

    if cv2.waitKey(1) == 13:
        break

vs.release()
video.release()

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
plt.plot(frame_array, area_array, color='g')
plt.plot(frame_array, speed_array, color='b')

# save the output into csv
df = pandas.DataFrame(data={"frame": frame_array, "area": area_array, "speed": speed_array})
df.to_csv("./Video/areavsspeed.csv", sep=',', index=False)

plt.show()

cv2.destroyAllWindows()
