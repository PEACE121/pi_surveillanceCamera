#!/bin/bash

(crontab -l ; echo "*/5 * * * * /home/pi/pitools/pitools/wlanRestart/wlanRestartScript.sh ") | sort - | uniq - | crontab -
