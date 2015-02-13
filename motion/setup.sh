#!/bin/bash

sudo cp motion /usr/local/bin/
(crontab -l ; echo "@reboot screen -S Motion -dmS sudo motion -c /home/pi/pitools/pitools/motion.conf") | sort - | uniq - | crontab -
