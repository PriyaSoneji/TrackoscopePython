import datetime
import threading
import tkinter as tk
from tkinter import *
import cv2

# define tracking variables
x = 0
y = 0
w = 0
h = 0
W = 0
H = 0

# define stuff for x-coordinate detection
ovcenterx = 0
smallx = 0
largex = 0
oldxdirection = 'N'
newxdirection = 'N'
xdirection = 'N'
centerx = 0

# define stuff for y-coordinate detection
ovcentery = 0
smally = 0
largey = 0
oldydirection = 'N'
newydirection = 'N'
ydirection = 'N'
centery = 0

# flipping variables
portopen = bool(False)
rotate = bool(False)
sendrepeat = bool(False)
centered = bool(False)
tracking = bool(False)
trackingsuccess = bool(False)
showOverlay = bool(True)
speedMode = bool(True)

# range limits
xrangehl = 60
xrangell = 40
yrangehl = 60
yrangell = 40

# graphing stuff
currx = 0
curry = 0

# Z-Axis
zdirection = 'N'
blurry = bool(False)
rightDirection = bool(False)
focus = 0
originalFocus = 0
compareFocus = 0

x_values = []
y_values = []
z_values = []
timestamps = []

if len(x_values) == 0:
    x_values.append(0)
if len(y_values) == 0:
    y_values.append(0)
if len(z_values) == 0:
    z_values.append(0)

if len(timestamps) == 0:
    now = datetime.datetime.now()
    timestamp = str(now.strftime("%H:%M:%S"))
    timestamps.append(timestamp)

availvid = []

trackinginZ = bool(False)

# initialize the window toolkit along with the two image panels
root = Tk()
panelA = None
panelB = None
frame = None
thread = None
thread2 = None
stopEvent = threading.Event()

count = 0
countmax = 10
countgraph = 0
countgraphmax = 30

# function to create our object tracker
tracker = cv2.TrackerCSRT_create()

# initialize the bounding box coordinates
initBB = None

fps = None
infovar = None

# the micrometers per send
basestepsize = 86.24
incrementstepxy = basestepsize / 2

figure1 = None
ax = None
bar1 = None

vs = None
