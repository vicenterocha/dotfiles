#!/usr/bin/env bash

CON=$( nmcli con | grep TUI | grep "\-\-" )
echo $CON

# if CON is empty then we are connected to the VPN
if [[ ! -z $CON ]]; then
    nmcli con up id TUI
    #sudo route add -net default gw 172.27.248.1 netmask 0.0.0.0 dev tun0 metric 800
    #sudo route del -net default gw 172.27.248.1 netmask 0.0.0.0 dev tun0 metric 50
else
    nmcli con down id TUI
fi

exit 0
