import serial
from time import sleep
print('opening port')
ser1 = serial.Serial('/dev/ttyACM0', 115200)
print(ser1)
print('sending command')
ser1.write(("R").encode())
print('waiting')
sleep(2)
print('sending stop')
ser1.write("S".encode())
print('done')
