#!/usr/bin/env bash

CON=$( nmcli con | grep "COCUS-AG" | grep "\-\-" )
echo $CON

# if CON is empty then we are connected to the VPN
if [[ ! -z $CON ]]; then
    nmcli con up id COCUS-AG
else
    nmcli con down id COCUS-AG
fi

exit 0
