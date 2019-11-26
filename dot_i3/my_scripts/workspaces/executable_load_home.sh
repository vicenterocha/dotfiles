#!/usr/bin/env bash

i3-msg "workspace 1; append_layout ~/.i3/workspaces/home_v2.json"

terminator -e 'tmux new -d -s rtv 'rtv' \; attach \;' &
terminator -e 'tmux new -d -s gtop 'gtop' \; attach \;' &

thunderbird > /dev/null 2>&1 &
