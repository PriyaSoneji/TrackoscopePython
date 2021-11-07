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
from src_new.zaxis import *

rotate = bool(False)
sendrepeat = bool(False)
centered = bool(False)
tracking = bool(False)
trackingsuccess = bool(False)
showOverlay = bool(True)
speedMode = bool(True)

root = Tk()
panelA = None
panelB = None
frame = None
thread = None
thread2 = None
stopEvent = threading.Event()


def button_init():
    # define the buttons and their commands
    startButton = Button(root, text="Start Tracking", command=startTracking, activebackground='yellow')
    plotButton = Button(root, text="Plot Graph", command=plotgraph, activebackground='yellow')
    zFocusButton = Button(root, text="Focus", command=focusing, activebackground='yellow')
    speedButton = Button(root, text="Change Speed Mode", command=changeSpeedMode, activebackground='yellow')
    dataButton = Button(root, text="Save Data", command=dataSave, activebackground='yellow')
    hideButton = Button(root, text="Change Overlay", command=changeOveraly, activebackground='yellow')
    blurButton = Button(root, text="Check Blur", command=calculateBlur, activebackground='yellow')
    infoLabel = Label(root, textvariable=infovar, font=("Times", 16))
    # buttons to control the movement
    yposButton = Button(root, text="Y+", command=yPos, activebackground='yellow')
    ynegButton = Button(root, text="Y-", command=yNeg, activebackground='yellow')
    xposButton = Button(root, text="X+", command=xPos, activebackground='yellow')
    xnegButton = Button(root, text="X-", command=xNeg, activebackground='yellow')
    zposButton = Button(root, text="Z+", command=zPos, activebackground='yellow')
    znegButton = Button(root, text="Z-", command=zNeg, activebackground='yellow')
    stopmovButton = Button(root, text="S", command=stopMov, activebackground='yellow')
    # place the buttons
    startButton.grid(row=1, column=0, sticky='WENS')
    plotButton.grid(row=1, column=1, sticky='WENS')
    zFocusButton.grid(row=2, column=0, sticky='WENS')
    speedButton.grid(row=2, column=1, sticky='WENS')
    dataButton.grid(row=3, column=0, sticky='WENS')
    hideButton.grid(row=3, column=1, sticky='WENS')
    blurButton.grid(row=4, column=1, sticky='WENS')
    yposButton.grid(row=1, column=3, sticky='WENS')
    ynegButton.grid(row=3, column=3, sticky='WENS')
    xposButton.grid(row=2, column=4, sticky='WENS')
    xnegButton.grid(row=2, column=2, sticky='WENS')
    zposButton.grid(row=4, column=4, sticky='WENS')
    znegButton.grid(row=4, column=2, sticky='WENS')
    stopmovButton.grid(row=2, column=3, sticky='WENS')
    infoLabel.grid(row=4, column=0, sticky='WENS')


def setFocusLabel():
    global focus, infovar
    infovar.set("Focus: " + str(focus))


def changeOveraly():
    global showOverlay
    showOverlay = not showOverlay
    if showOverlay:
        infovar.set("Showing Tracker")
    else:
        infovar.set("Just Showing Video")


def changeSpeedMode():
    global speedMode
    speedMode = not speedMode
    if speedMode:
        infovar.set("Set to Optimal Speed")
    else:
        infovar.set("Now Full Stop in Between")
