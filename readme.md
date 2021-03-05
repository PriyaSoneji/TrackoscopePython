# Trackoscope Program
  
## Descriptions of Each Program:

### Trackoscope.py (MAIN PROGRAM)
This program is to be run on a laptop. It has the full object-tracking capability and has a user-friendly GUI.

### Grapher.py
Taking CSV data and converting to meaningful graphs

### AutoFocus.py
This program is to be run on a Raspberry Pi. Uses Picamera library and the Arducam Autofocus Replacement on the Raspberry Pi V2 Camera to autofocus and capture the most focused image.

### TrackoscopeRPN.py
This program is to be run on a laptop. It has the full object-tracking capability and has a user-friendly GUI. Opposed to the csrt tracker, this uses a faster neural net tracker (DiSiamRPN)

### PiFPSTest.py
This program is to be run on a Raspberry Pi with a Raspberry Pi Camera. Optimizes FPS through threading. Max FPS achieved: 160 fps

### Tracking_Rasp.py
This program is to be run on a Raspberry Pi. It has limited object-tracking capability and has a user-friendly GUI. Uses a Pi Camera library to try and optimize FPS.

### NonGUITracking.py
This program is to be run on a laptop. It is the earliest stage of object-tracking.

## Getting Started
This project uses python virtual environments

Open a command prompt and then install the dependencies to get it working.

    pip install -r requirements.txt
    
    
### Materials
* Arduino Uno
* CNC Shield
* 3 NEMA 17 Stepper Motors
* Webcam/USB Camera


