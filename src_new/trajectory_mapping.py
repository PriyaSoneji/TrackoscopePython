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
from src_new.basic_tracking import *
from src_new.zaxis import *

count = 0
countmax = 10
countgraph = 0
countgraphmax = 30

bar1 = None

timestamps = []
now = datetime.datetime.now()
timestamp = str(now.strftime("%H:%M:%S"))
timestamps.append(timestamp)


# add points to the graph and updates plot
def addpoint():
    global count, countmax, figure1, zval, countgraph, countgraphmax, timestamps
    if count == countmax:
        add_x_val(round(currx, 2))
        add_y_val(round(curry, 2))
        add_z_val(round(zval, 2))
        now = datetime.datetime.now()
        timestamp = str(now.strftime("%H:%M:%S"))
        timestamps.append(timestamp)
        count = 0
    if countgraph == countgraphmax:
        plotgraph()
        countgraph = 0
    count = count + 1
    countgraph = countgraph + 1


def def_fig1():
    # figure one data
    figure1 = plt.Figure(figsize=(6, 5), dpi=100)
    if get_trackinginZ():
        ax = figure1.add_subplot(111, projection='3d')
    else:
        ax = figure1.add_subplot(111)
    bar1 = FigureCanvasTkAgg(figure1, root)
    bar1.get_tk_widget().grid(row=0, column=1)


def dataSave():
    global timestamps
    if get_trackinginZ():
        df = pandas.DataFrame(
            data={"xval": get_x_vals(), "yval": get_y_vals(), "zval": get_z_vals(), "time": timestamps})
        df.to_csv("./trackingvals.csv", sep=',', index=False)
    else:
        df = pandas.DataFrame(data={"xval": get_x_vals(), "yval": get_y_vals(), "time": timestamps})
        df.to_csv("./trackingvals.csv", sep=',', index=False)


# plots the graph using matplotlib
def plotgraph():
    # grab a reference to the image panels
    global panelA, figure1, ax, root

    ax.cla()

    # plot
    if get_trackinginZ():
        ax.plot(get_x_vals(), get_y_vals(), get_z_vals(), color='black', linestyle='solid', marker='+',
                markerfacecolor='blue', markevery=[-1])
        ax.set_xlabel('X-Movement (μm)')
        ax.set_ylabel('Y-Movement (μm)')
        ax.set_zlabel('Z-Movement (μm)')
    else:
        ax.plot(get_x_vals(), get_y_vals(), color='green', linestyle='solid', marker='H',
                markerfacecolor='blue', markersize=8, markevery=[-1])
        ax.set_xlabel('X-Movement (μm)')
        ax.set_ylabel('Y-Movement (μm)')

    # idle draw
    bar1.draw_idle()
