#!/usr/bin/env python3
import pyudev
import os
import traceback

context = pyudev.Context()
BUDS_BL_ADDR = os.environ["BUDS_BL_ADDR"]
BUDS_ADDR = "\"" + BUDS_BL_ADDR + "\""

SS60_BL_ADDR = os.environ["SS60_BL_ADDR"]
SS60_ADDR = "\"" + SS60_BL_ADDR + "\""

monitor = pyudev.Monitor.from_netlink(context)
for type, device in monitor:
    try:
        devpath = device.get("DEVPATH")
        device_name = device.get("NAME")
        if device_name == BUDS_ADDR or device_name == SS60_ADDR:
            print("Found {}".format(device_name))
            try:
                if type == 'add':
                    # mute speakers, so sound never leaks from the speakers, due to a small delay until buds are ready
                    os.system("pactl set-sink-mute alsa_output.pci-0000_00_1f.3.analog-stereo true")
                    os.system("/usr/bin/playerctl play")
                    print('Buds connected. Playing')
                else:
                    os.system("/usr/bin/playerctl pause")
            except:
                traceback.print_stack()
                pass
    except:
        traceback.print_stack()
        pass
