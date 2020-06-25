# Trackoscope Program
  
## Descriptions of Each Program:

### AutoFocus.py
This program is to be run on a Raspberry Pi. Uses Picamera library and the Arducam Autofocus Replacement on the Raspberry Pi V2 Camera to autofocus and capture the most focused image.

### GUI_tracking.py
This program is to be run on a laptop. It has the full object-tracking capability and has a user-friendly GUI (work-in-progress)

### PiFPSTest.py
This program is to be run on a Raspberry Pi with a Raspberry Pi Camera. Optimizes FPS through threading.

### Tracking_Rasp.py
This program is to be run on a Raspberry Pi. It has limited object-tracking capability and has a user-friendly GUI. Treats the Pi Camera as a webcam. There is current issues with communicating to the Arduino (work-in-progress)

### Tracking_RaspFPSOpt.py
This program is to be run on a Raspberry Pi. It has limited object-tracking capability and has a user-friendly GUI. Uses a Pi Camera library to try and optimize FPS. There is current issues with communicating to the Arduino (work-in-progress)

### object_tracking.py
This program is to be run on a laptop. It is the earliest stage of object-tracking.

### simpleMove.py
This program is to be run on a Raspberry Pi. It is used to debug the issue regarding failure to send instructions to the Arduino.

## Getting Started
This project uses python virtual environments

Open a command prompt and then install the dependencies to get it working.

    pip install -r requirements.txt
    
    
### Materials
* Arduino Uno
* CNC Shield
* 3 NEMA 17 Stepper Motors
* Raspberry Pi
* Pi Camera


