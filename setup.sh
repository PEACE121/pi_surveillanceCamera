#!/bin/bash

sudo apt-get update

# motion
cd motion
sudo chmod +x setup.sh
sudo ./setup.sh
cd /home/pi/pi_surveillanceCamera 

#wringPi (for light)
cd wiringPi
./build
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
