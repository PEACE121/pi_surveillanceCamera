#!/bin/bash

# motion
cd motion
sudo chmod +x setup.sh
sudo ./setup.sh
cd ..

# pan tilt configuration
cd panTilt
cp pi_pan_tilt_commandline.py /home/pi
cd ..

# wlan restart script
cd wlanRestart
sudo chmod +x setup.sh
sudo ./setup.sh
cd ..
