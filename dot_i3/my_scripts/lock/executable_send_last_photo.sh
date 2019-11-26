#!/usr/bin/env bash

/home/$USER/.i3/my_scripts/lock/cam_pamd.sh
image=$( find /home/$USER/.i3/my_scripts/lock/recs -printf '%p\n' | sort -r | head -n 1 )
/home/$USER/.i3/my_scripts/pushbullet/send_image.py "$image"

exit 0
