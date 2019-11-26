#!/usr/bin/env bash

sudo route add -net default gw 172.27.248.1 netmask 0.0.0.0 dev tun0 metric 800
sudo route del -net default gw 172.27.248.1 netmask 0.0.0.0 dev tun0 metric 50

exit 0
