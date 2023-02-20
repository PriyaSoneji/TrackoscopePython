import cv2
import matplotlib.pyplot as plt
import numpy as np
import imutils
import pandas

# Read the original image
img = cv2.imread('./Video/Images/CNFT2.tif')
img = imutils.resize(img, width=500)
# Display original image
cv2.imshow('Original', img)

sharpen_filter = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
sharped_img = cv2.filter2D(img, -1, sharpen_filter)
cv2.imshow('Sharp', sharped_img)

# Canny Edge Detection
canny = cv2.Canny(image=sharped_img, threshold1=100, threshold2=150)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
canny = cv2.dilate(canny, kernel, iterations=1)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
canny = cv2.erode(canny, kernel, iterations=1)

cv2.imshow('Canny Edge Detection', canny)

cv2.waitKey(0)
cv2.destroyAllWindows()
