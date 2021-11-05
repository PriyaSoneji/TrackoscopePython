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


# check for available serial ports
def serial_ports():
    # List serial ports
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(50)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def open_comm():
    # open Arduino Serial
    availableport = serial_ports()
    if len(availableport) > 0:
        # ser1 = serial.Serial(availableport[0], 2000000)
        ser1 = serial.Serial("COM3", 2000000)
        sleep(1)
        ser1.flush()
        sleep(2)
        portopen = True


def sendCommand(cmd):
    global portopen, ser1
    if portopen:
        ser1.write(cmd)


def sendCommandT(cmd):
    global portopen, ser1
    if portopen:
        thread3 = threading.Thread(target=sendCommandThread, args=(cmd, ser1))
        thread3.start()


# sends command to the Arduino over serial port
def sendCommandThread(cmd, serport):
    serport.write(cmd)
    print("sent command")


def yPos():
    sendCommand('D'.encode())


def yNeg():
    sendCommand('U'.encode())


def xPos():
    sendCommand('R'.encode())


def xNeg():
    sendCommand('L'.encode())


def zPos():
    sendCommand('t'.encode())


def zNeg():
    sendCommand('b'.encode())


def stopMov():
    sendCommand('S'.encode())


def hardStop():
    sendCommand('E'.encode())
    ser1.flush()
