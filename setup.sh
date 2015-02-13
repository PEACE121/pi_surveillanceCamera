#!/bin/bash

# motion
cd motion
sudo chmod +x setup.sh
sudo ./setup.sh
cd ..

# pan tilt configuration
cd panTilt
sudo ./setup.sh
cd ..

# wlan restart script
cd wlanRestart
sudo chmod +x setup.sh
sudo ./setup.sh
cd ..
