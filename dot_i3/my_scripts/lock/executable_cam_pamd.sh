#!/usr/bin/env bash

#xs=`date +%s`
#xs=`date +%d/%m/%Y %H:%M:%S`


ts=$(date '+%d%m%Y-%H%M%S');
day=$(date '+%d%m%Y');

echo "$ts" >> /home/$USER/.i3/my_scripts/lock/logs/log.txt
mkdir /home/$USER/.i3/my_scripts/lock/recs/"$day"

ffmpeg -f video4linux2 -s vga -i /dev/video0 -vframes 10 /home/$USER/.i3/my_scripts/lock/recs/"$day"/vid-"$ts".%01d.jpg

exit 0
