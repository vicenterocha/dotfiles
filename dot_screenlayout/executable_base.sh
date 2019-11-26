#!/bin/bash

export DISPLAY=":0"
echo Display Exported

EDPON=$( xrandr --query | grep -w 'eDP1 connected' )
echo xranrd - $EDPON.
DPON=$( xrandr --query | grep -w 'DP1 connected' )
echo xranrd - $DPON.
HDMI1ON=$( xrandr --query | grep -w 'HDMI1 connected' )
echo xranrd - $HDMI1ON.

if [[ -z $HDMI1ON ]] && [[ ! -z $DPON ]] && [[ ! -z $EDPON ]]; then
    echo "eDP1 and DP1 connected"
    xrandr --output VIRTUAL1 --off --output eDP1 --mode 1920x1080 --pos 2560x0 --rotate normal --output DP1 --primary --mode 2560x1440 --pos 0x0 --rotate normal --output HDMI3 --off --output HDMI2 --off --output HDMI1 --off --output DP2 --off
elif [[ ! -z $HDMI1ON ]] && [[ -z $DPON ]] && [[ ! -z $EDPON ]]; then
    echo "eDP1 and HDMI11 connected"
    xrandr --output eDP1 --primary --mode 1920x1080 --pos 2560x0 --rotate normal --output DP1 --off --output DP2 --off --output HDMI1 --mode 2560x1440 --pos 0x0 --rotate normal --output HDMI2 --off --output HDMI3 --off --output VIRTUAL1 --off
    #xrandr --output eDP1 --primary --mode 1920x1080 --pos 0x0 --rotate normal --output DP1 --off --output DP2 --off --output HDMI1 --mode 1920x1080 --pos 1920x0 --rotate normal --output HDMI2 --off --output HDMI3 --off --output VIRTUAL1 --off
elif [[ ! -z $HDMI1ON ]] && [[ ! -z $DPON ]] && [[ ! -z $EDPON ]]; then
    echo "DP1, eDP1 and HDMI11 connected"
    xrandr --output eDP1 --mode 1920x1080 --pos 5120x0 --rotate normal --output DP1 --primary --mode 2560x1440 --pos 0x0 --rotate normal --output DP2 --off --output HDMI1 --mode 2560x1440 --pos 2560x0 --rotate normal --output HDMI2 --off --output HDMI3 --off --output VIRTUAL1 --off
else
    echo "DP1 disconnected"
    xrandr --output VIRTUAL1 --off --output eDP1 --mode 1920x1080 --pos 2560x0 --rotate normal --output DP1 --off --output HDMI3 --off --output HDMI2 --off --output HDMI1 --off --output DP2 --off
fi

feh --bg-fill ~/Pictures/3_Firewatch.jpg

