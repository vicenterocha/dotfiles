#!/usr/bin/env python
from pushbullet import Pushbullet
import sys
import os

PUSHBULLET_API_KEY = os.environ["PUSHBULLET_API_KEY"]

def send_note():

    if len(sys.argv) < 3:
        print('Missing arguments')
        return

    title = sys.argv[1]
    body = sys.argv[2]

    pb = Pushbullet(PUSHBULLET_API_KEY)
    device = pb.get_device('S10')
    push = pb.push_note(title, body, device=device)

if __name__ == '__main__':
    send_note()
