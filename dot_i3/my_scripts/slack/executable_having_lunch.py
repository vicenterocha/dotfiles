#!/usr/bin/env python

import requests
import json
from datetime import datetime, timedelta
import calendar
import os

slack_token = os.environ['SLACK_TOKEN']


def update_slack_status(message="Lunch break", emoji=":pizza:", expiration=0):
    """ Changes the status of my slack profile

    :return: response
    """
    status_text, status_emoji = check_slack_status()
    if status_text == message and status_emoji == emoji:
        print('Status unchanged. Not updating.')
        return 'Status unchanged. Not updating.'

    headers = {"Authorization": "Bearer " + slack_token,
               'Content-Type': 'application/json'}
    data = {
        "profile": {
            "status_text": message,
            "status_emoji": emoji,
            "status_expiration": expiration
        }
    }
    r = requests.post("https://slack.com/api/users.profile.set", data=json.dumps(data), headers=headers)
    if r.status_code == 200:
        profile = json.loads(r.text)['profile']
        print('New status text:', profile['status_text'])
        print('New status emoji:', profile['status_emoji'])

    return r

def check_slack_status():
    """Checks the status of my slack profile

    :return: if ok, status text and emoji else response code and reason
    """
    headers = {"Authorization": "Bearer " + slack_token,
               'Content-Type': 'application/json'}
    r = requests.get("https://slack.com/api/users.profile.get", headers=headers)

    if r.status_code == 200:
        profile = json.loads(r.text)['profile']
        return profile['status_text'], profile['status_emoji']
    else:
        return r.status_code, r.reason

if __name__ == '__main__':
    d = datetime.utcnow() + timedelta(hours=1) # get next hour
    unixtime = calendar.timegm(d.utctimetuple())

    # it will update the status to expire at the next hour O'clock
    update_slack_status(expiration=unixtime)

