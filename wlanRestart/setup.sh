#!/bin/bash

(crontab -l ; echo "*/5 * * * * /home/pi/pi_surveillanceCamera/wlanRestart/wlanRestartScript.sh ") | sort - | uniq - | crontab -
