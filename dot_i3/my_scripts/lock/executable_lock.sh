#!/usr/bin/env bash

# Enable compton's fade-in effect so that the lockscreen gets a nice fade-in
# effect.
#dbus-send --print-reply --dest=com.github.chjj.compton.${DISPLAY/:/_} / \
#        com.github.chjj.compton.opts_set string:no_fading_openclose boolean:false

# If disable unredir_if_possible is enabled in compton's config, we may need to
# disable that to avoid flickering. YMMV. To try that, uncomment the following
# two lines and the last two lines in this script.
# dbus-send --print-reply --dest=com.github.chjj.compton.${DISPLAY/:/_} / \
#     com.github.chjj.compton.opts_set string:unredir_if_possible boolean:false

# Suspend dunst and lock, then resume dunst when unlocked.
pkill -u $USER -USR1 dunst

screen='/tmp/screen.png'
scrot "$screen"

#/home/$USER/.i3/my_scripts/lock/monitor_keys.sh &
#i3lock -n -u -i "$screen"

{ # try
    /usr/bin/playerctl pause
} || { # catch
	echo damn
}
slock
