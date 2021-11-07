# make sure bluetooth is off
import tkinter as tk
from tkinter import *
from PIL import Image
from PIL import ImageTk
import imutils
import threading
import cv2
from time import sleep
import serial
import pyautogui
import pandas
import glob
import numpy as np
from imutils.video import VideoStream
from imutils.video import FPS
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
from src_new.arduino_communication import *
from src_new.basic_tracking import *
from src_new.trajectory_mapping import *
from src_new.initialization import *
from src_new.gui import *

trackinginZ = bool(False)
z_values = []


# checks for bluriness
def variance_of_laplacian(image):
    # compute the Laplacian of the image and then return the focus
    # measure, which is simply the variance of the Laplacian
    return cv2.Laplacian(image, cv2.CV_64F).var()


def fft_blur_detection(image, thresh):
    (h, w) = image.shape
    (cX, cY) = (int(w / 2.0), int(h / 2.0))

    fft = np.fft.fft2(image)
    fftShift = np.fft.fftshift(fft)

    fftShift[cY - 60:cY + 60, cX - 60:cX + 60] = 0
    fftShift = np.fft.ifftshift(fftShift)
    recon = np.fft.ifft2(fftShift)

    magnitude = 20 * np.log(np.abs(recon))
    mean = np.mean(magnitude)

    return mean, mean <= thresh


blurcap = 24
ogfocus = 0


def focusing():
    global blurry
    calculateBlur()
    if blurry:
        fixBlurMotor()


def threadedZAxis():
    while not stopEvent.is_set():
        # Z-Axis Detection
        focusing()
        sleep(2)


# calculates the blur and returns the blur number
def calculateBlur():
    global focus, blurry, blurcap, tracking, x, y, w, h, vs
    if tracking:
        image = vs.read()
        image = image[y:y + h, x:x + w]
    else:
        image = vs.read()

    image = vs.read()

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    focus = round(variance_of_laplacian(gray), 2)
    # focus = round(cv2.Laplacian(image, cv2.CV_64F).var(), 2)
    if focus > blurcap:
        blurry = bool(False)
    else:
        blurry = bool(True)

    # (focus, blurry) = fft_blur_detection(gray, blurcap)
    # focus = round(focus, 2)

    setFocusLabel()
    return focus


updowncount = 0
zval = 0


# uses a motor to fix the blur
def fixBlurMotor():
    global originalFocus, compareFocus, rightDirection, focus, zdirection, blurcap, ogfocus, updowncount, zval, incrementstepxy
    rightDirection = bool(True)
    zdirection = 'b'
    ogfocus = focus
    originalFocus = focus
    updowncount = zval
    for j in range(20):
        sleep(0.50)
        compareFocus = calculateBlur()

        if abs(compareFocus - originalFocus) > 0.5:
            if compareFocus > originalFocus:
                rightDirection = bool(True)
            else:
                rightDirection = bool(False)
            originalFocus = focus
        elif ((blurcap - compareFocus) - (blurcap - ogfocus)) > 1:
            # print("too far")
            rightDirection = bool(False)

        if not blurry:
            print("focused now")
            zdirection = 'S'
            sendCommand(zdirection.encode())
            break

        if not rightDirection:
            # print("Change")
            if zdirection == 't':
                zdirection = 'b'
            else:
                zdirection = 't'

        if zdirection == 't':
            updowncount = updowncount + incrementstepxy
        else:
            updowncount = updowncount - incrementstepxy

        sendCommand(zdirection.encode())

    zval = updowncount
    addpoint()
    print("ended")
