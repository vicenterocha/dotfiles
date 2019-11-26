#!/usr/bin/env bash

echo started, sleeping 10 seconds
sleep 10
xinput test-xi2 --root | while read in ; do
    if [[ $in = *"EVENT"*  ]]; then
        echo key press detected
        res=$( pgrep -f i3lock )
        if [[ -z $res ]]; then
            exit 0
        fi
        #/home/$USER/.i3/my_scripts/lock/send_last_photo.sh
        echo i3lock active, sent photo
    sleep 10
    fi
done

exit 0
