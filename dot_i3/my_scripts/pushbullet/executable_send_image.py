#!/usr/bin/env python
from pushbullet import Pushbullet
import sys
import os

PUSHBULLET_API_KEY = os.environ["PUSHBULLET_API_KEY"]

def send_image():

    if len(sys.argv) < 2:
        print('Missing image in arguments')
        return

    pb = Pushbullet(PUSHBULLET_API_KEY)
    image = sys.argv[1]
    with open(image, "rb") as pic:
        file_data = pb.upload_file(pic, "photo.jpg")

    device = pb.get_device('S10')
    push = pb.push_file(**file_data, device=device)

if __name__ == '__main__':
    send_image()
