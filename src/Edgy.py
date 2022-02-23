import numpy as np
import cv2
import matplotlib.pyplot as plt
import imutils
import pandas

# define source of video and blank arrays
vs = cv2.VideoCapture("./Video/Stentor_Stop_Go_Raw_Cropped.mp4")

# loop through the frames of the video
while True:
    ret, frame = vs.read()

    # edge detection
    try:
        # resize video frame
        frame = imutils.resize(frame, width=700)
    except:
        break

    newbinary = np.zeros((frame.shape[0], frame.shape[1]))
    # d = np.array((img.shape[0],img.shape[1]))

    # convert to gray scale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    (thresh, binary) = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # filter size 7x7
    filterK = np.ones((3, 3))
    # print(filterK)

    # shape of image and kernel
    S = binary.shape
    F = filterK.shape

    # convert into 0 and 1
    binary = binary / 255

    # for padding get row and column
    R = S[0] + F[0] - 1
    C = S[1] + F[1] - 1

    # get the new padding image in only zeros
    N = np.zeros((R, C))

    # insert the image
    for i in range(S[0]):
        for j in range(S[1]):
            N[i + np.int((F[0] - 1) / 2), j + np.int((F[1] - 1) / 2)] = binary[i, j]

    # use the filter for erosion
    for i in range(S[0]):
        for j in range(S[1]):
            k = N[i:i + F[0], j:j + F[1]]
            result = (k == filterK)
            final = np.all(result == True)
            if final:
                newbinary[i, j] = 1
            else:
                newbinary[i, j] = 0

    # use filter for dialation
    for i in range(S[0]):
        for j in range(S[1]):
            k = N[i:i + F[0], j:j + F[1]]
            result = (k == filterK)
            final = np.any(result == True)
            if final:
                newbinary[i, j] = 1
            else:
                newbinary[i, j] = 0

    d = binary - newbinary

    # show live preview
    cv2.imshow('Video feed', d)

    if cv2.waitKey(1) == 13:
        break

vs.release()
cv2.destroyAllWindows()
