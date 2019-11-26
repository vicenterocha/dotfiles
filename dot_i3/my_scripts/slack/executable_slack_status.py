#!/usr/bin/env python
import json
import requests
import subprocess
import os

location_api_key = os.environ["LOCATION_API_KEY"]
lambda1_url = ' https://trnx0m4r59.execute-api.eu-west-2.amazonaws.com/default/slack_status_automator'

houses = ['casa', 'fabrica', '59233E']
office = ['cocus']


def get_ssid():
    """
    """
    cmd = "iw dev wlo1 link | grep SSID"
    ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ssid = ps.communicate()[0].decode('utf-8')

    if any(nw in ssid.lower() for nw in office):
        print(ssid, 'office')
        # return "OFFICE"
        return "HOME"
    elif any(nw in ssid.lower() for nw in houses):
        print(ssid, 'home')
        return "HOME"
    else:
        print(ssid, 'moon')
        return "MOON"


def send_location_info(location):
    """ Send location to AWS Lambda Slack State Change

    :return: response
    """

    headers = {"x-api-key": location_api_key}

    data = {
        "location": location
    }

    r = requests.post(lambda1_url, json=data, headers=headers)

    if r.status_code == 200:
        text = json.loads(r.text)
        print(text)
    else:
        print('Sum Ting Wong')
        text = json.loads(r.text)

    return r


location = get_ssid()
send_location_info(location)

