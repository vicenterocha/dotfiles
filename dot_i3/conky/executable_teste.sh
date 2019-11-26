#!/usr/bin/env bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

ssh -q -o BatchMode=yes -o ConnectTimeout=10 root@172.26.214.111 exit

if [ $? -ne 0 ]
then
    echo " "
else
    echo " "
    notify-send -u critical -i info '111 UP'
fi

ssh -q -o BatchMode=yes -o ConnectTimeout=10 root@172.26.214.112 exit

if [ $? -ne 0 ]
then
    break
else
    notify-send -u critical -i info '112 UP'
fi
