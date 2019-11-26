#!/usr/bin/env python

import bluetooth
import sys
import os
import math
import time
import subprocess
import re
import sqlite3
from sqlite3 import Error
from datetime import datetime
from sqlite_api import update_bluetooth_status
from sqlite_api import read_bluetooth_status
from pushbullet import Pushbullet

"""
#########
# CONKY #
#########

Read database entry for symbol and show it

##########
# PYTHON #
##########

Run constantly approach:
    - while true, with a 2 seconds sleep
    - So, every 2 seconds the state of the bluetooth connection is checked
    - Connection state and strength is written to an array
    - After 10 seconds (5 verifications):
        if AVG is lower than X
            lock
        else
            clean



    - examples:

        | 0 | 0 | 0 | 0 | 0 |
            avg = 0
            sum = 0
        log(0.1) + log(0.1) + log(0.1) + log(0.1) + log(0.1) = -5

        | 0 | 0 | 0 | -1 | -10 |
            avg = -2.2
            sum = -11
        log(0.1) + log(0.1) + log(0.1) + log(1) + log(10) = -2

        | 0 | 0 | -1 | -1 | -2 |
            avg = -0.8
            sum = -4
        log(0.1) + log(0.1) + log(1) + log(1) + log(2) = -1.699

        | 0 | 0 | 0 | -10 | -10 |
            avg = -4.4
            sum = -21
        log(0.1) + log(0.1) + log(0.1) + log(10) + log(10) = −0,958607315

        | -1 | -1 | -1 | -1 | -2 |
            sum = 6
        log(1)+log(1)+log(1)+log(1)+log(2) = 0.301

        | 0 | 0 | -10 | -10 | -10 |
            avg = -6
            sum = -30
        log(0.1) + log(0.1) + log(10) + log(10) + log(10) = 1

        | -4 | -3 | -5 | -6 | -10 |
            avg = -5.6
            sum = -28
        log(4) + log(3) + log(5) + log(6) + log(10) = 3.55630


        math.log10()

        Conclusion, > 0 is probably a sufficient condition for locking the device


"""

PORT = 3  # bluetooth port
ADDR = os.environ["S10_BL_ADDR"] # device bluetooth address
USER = os.environ["USER"]
LOCKER = '/home/' + USER + '/.i3/my_scripts/lock/lock.sh'  # system locker
# LOCKER = 'slock'  # system locker - CHANGE THIS
DISCONNECTED_WEIGHT = 15
LOCK_SENSITIVITY = 3
PUSHBULLET_API_KEY = os.environ["PUSHBULLET_API_KEY"]


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        # print(sqlite3.version)
        return conn
    except Error as e:
        print(e)


def notify_computer(message):
    """
    sends system notification
    """
    subprocess.Popen(['notify-send', message])


def connection_check():
    """
    checks if device is connected. Returns True if connected, else False
    """
    ps = subprocess.Popen(['hcitool', 'con'], stdout=subprocess.PIPE)
    device = ps.communicate()[0].decode('utf-8')

    if ADDR in device:
        return True
    else:
        return False


def proximity_check():
    """
    checks if device is nearby, returns rssi value
    """
    ps = subprocess.Popen(['hcitool', 'rssi', ADDR], stdout=subprocess.PIPE)
    proximity = ps.communicate()
    if proximity[0]:
        proximity = proximity[0].decode('utf-8')
    else:
        return -DISCONNECTED_WEIGHT
    proximity = [int(d) for d in re.findall(r'-?\d+', proximity)]

    if proximity[0] > 0:
        return 0

    return proximity[0]


def notify_s10(title, body):
    pb = Pushbullet(PUSHBULLET_API_KEY)
    device = pb.get_device('S10')
    push = pb.push_note(title, body, device=device)
    print('Notified')


def get_login_time():
    cmd = "last | tac | grep pts | tail -n 1"
    ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = ps.communicate()[0].decode('utf-8')
    day = output.split()[5]
    hour_minute = output.split()[6].split(':')
    hour = hour_minute[0]
    minute = hour_minute[1]
    return day, hour, minute


def get_system_boot_time():
    cmd = "last | tac | grep \"system boot\" | tail -n 1"
    ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = ps.communicate()[0].decode('utf-8')
    day = output.split()[6]
    hour_minute = output.split()[7].split(':')
    hour = hour_minute[0]
    minute = hour_minute[1]
    return day, hour, minute


def can_lock():
    """
    TODO read day so that comparison when last login was on another day time comparison still makes sense
    """
    system_boot_time = get_system_boot_time()
    sb_day = system_boot_time[0]
    sb_hour = system_boot_time[1]
    sb_minute = system_boot_time[2]

    login_time = get_login_time()
    login_day = login_time[0]
    login_hour = login_time[1]
    login_minute = login_time[2]

    now = datetime.now().replace(second=0, microsecond=0)

    sb_time = now.replace(day=int(sb_day), hour=int(sb_hour), minute=int(sb_minute), second=0, microsecond=0)
    print('System boot time', sb_time.isoformat())
    login_time = now.replace(day=int(login_day), hour=int(login_hour), minute=int(login_minute), second=0, microsecond=0)
    print('Login time', login_time.isoformat())

    time_diff = (now - sb_time).total_seconds()
    if time_diff >= 30:
        # if already logged in
        if login_time > sb_time:
            return True
    return False


def lock_device(log_sum):
    """
    Locks device
    :param log_sum:
    :return:
    """

    # first check if locker has already been invoked, so it doesn't invoke infinite lockers
    # ps = subprocess.Popen(['pgrep', LOCKER], stdout=subprocess.PIPE)
    ps = subprocess.Popen(['pgrep', 'slock'], stdout=subprocess.PIPE)
    ps = ps.communicate()[0].decode('utf-8')
    if not ps:
        try:
            if read_bluetooth_status() != '':
                update_bluetooth_status(False)
                notify_s10('LOCKED', 'Weak signal..' + str(log_sum))
        except:
            print('Could not sent notification')

        time.sleep(1)  # without it notification would only arrive after unlock
        subprocess.Popen([LOCKER], stdout=subprocess.PIPE)
    print(read_bluetooth_status())


def try_to_connect():
    """
    Tries to connect to S10
    :return:
    """
    try:
        if not connection_check():  # if not connected, try to connect
            s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            s.connect((ADDR, PORT))
            print('Was not connected.')
    except:
        print('Some wrong')


status_history = []

while True:

    try_to_connect()

    prox = -proximity_check() + 0.1 if connection_check() else DISCONNECTED_WEIGHT  # negate and +0.1 so that log works fine
    print('Proximity is', str(prox))

    status_history += [prox]

    # checks bluetooth status every 10 seconds
    if len(status_history) == 5:
        print('Checking proximity log sum')

        result = sum(math.log10(v) for v in status_history)
        print('Log sum is', str(result))

        if result < LOCK_SENSITIVITY:
            update_bluetooth_status(True)
            print('All fine')
        else:
            if can_lock():
            # if True:
                print('Too weak')
                notify_computer('Weak signal.. Locking device..')
                time.sleep(2)
                lock_device(result)
            else:
                print('Just logged in. Waiting..')

        # reset status history
        status_history = []

    sys.stdout.flush()
    # wait 2 seconds
    time.sleep(2)
