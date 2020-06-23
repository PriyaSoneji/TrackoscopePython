import serial
from time import sleep

ser1 = serial.Serial('COM3', 9600)

sleep(2)
ser1.write('R'.encode())

sleep(3)

ser1.write('S'.encode())