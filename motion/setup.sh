#!/bin/bash

sudo apt-get install ffmpeg libav-tools libavcodec53 libavdevice53 libavfilter2 libavformat53 libavutil51 libdc1394-22 libdirac-encoder0 libgsm1 libmp3lame0 libmysqlclient18 libopencv-core2.3 libopencv-imgproc2.3 libpostproc52 libpq5 libraw1394-11 libschroedinger-1.0-0 libspeex1 libswscale2 libtheora0 libva1 libvpx1 libx264-123 libxvidcore4 mysql-common libjpeg62 screen

sudo cp motion /usr/local/bin/
(crontab -l ; echo "@reboot screen -S Motion -dmS sudo motion -c /home/pi/pi_surveillanceCamera/motion/motion.conf") | sort - | uniq - | crontab -
