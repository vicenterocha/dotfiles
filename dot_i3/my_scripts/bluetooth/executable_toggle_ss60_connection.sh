#!/usr/bin/env bash

# Get connected value (yes or no)
ON=$(bluetoothctl info $SS60_BL_ADDR | grep Connected | awk '{print $2}')
echo $ON

if [[ $ON == "yes" ]]; then
    bluetoothctl disconnect $SS60_BL_ADDR
else
    bluetoothctl connect $SS60_BL_ADDR
fi

exit 0
