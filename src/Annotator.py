import numpy
import cv2
import imutils

cap = cv2.VideoCapture('./Video/Spirostomum.mp4')

fourcc = cv2.VideoWriter_fourcc(*'DIVX')
out = cv2.VideoWriter('./Video/annotated.mp4', fourcc, 30.0, (1080, 720))
while 1:
    # read the frames
    ret, frame = cap.read()
    frame = imutils.resize(frame, width=1080)

    # A line
    cv2.rectangle(frame, (530, 450), (580, 455), (0, 0, 0), -1)

    cv2.putText(frame, "555 um", (530, 440), cv2.FONT_HERSHEY_COMPLEX_SMALL, .7, (0, 0, 0))
    out.write(frame)
    # if key pressed is 'Esc', exit the loop
    cv2.imshow('frame', frame)

    if cv2.waitKey(33) == 27:
        break

out.release()

cv2.destroyAllWindows()
