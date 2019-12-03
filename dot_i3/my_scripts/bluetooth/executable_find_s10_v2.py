#!/usr/bin/env python

from time import sleep

import bluetooth
import bluetooth._bluetooth as bt
import struct
import array
import fcntl

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

PORT = 3  # bluetooth port
ADDR = os.environ["S10_BL_ADDR"]  # device bluetooth address
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
    login_time = now.replace(day=int(login_day), hour=int(login_hour), minute=int(login_minute), second=0,
                             microsecond=0)
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


class BluetoothRSSI(object):
    """Object class for getting the RSSI value of a Bluetooth address.
    Reference: https://github.com/dagar/bluetooth-proximity
    """

    def __init__(self, addr):
        self.addr = addr
        self.hci_sock = bt.hci_open_dev()
        self.hci_fd = self.hci_sock.fileno()
        self.bt_sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        self.bt_sock.settimeout(10)
        self.connected = False
        self.cmd_pkt = None

    def prep_cmd_pkt(self):
        """Prepares the command packet for requesting RSSI"""
        reqstr = struct.pack(
            "6sB17s", bt.str2ba(self.addr), bt.ACL_LINK, b'\0' * 17)
        request = array.array("b", reqstr)
        handle = fcntl.ioctl(self.hci_fd, bt.HCIGETCONNINFO, request, 1)
        handle = struct.unpack("8xH14x", request.tostring())[0]
        self.cmd_pkt = struct.pack('H', handle)

    def connect(self):
        """Connects to the Bluetooth address"""
        self.bt_sock.connect_ex((self.addr, 1))  # PSM 1 - Service Discovery
        self.connected = True

    def get_rssi(self):
        """Gets the current RSSI value.
        @return: The RSSI value (float) or None if the device connection fails
                 (i.e. the device is nowhere nearby).
        """
        try:
            # Only do connection if not already connected
            if not self.connected:
                self.connect()
            if self.cmd_pkt is None:
                self.prep_cmd_pkt()
            # Send command to request RSSI
            rssi = bt.hci_send_req(
                self.hci_sock, bt.OGF_STATUS_PARAM,
                bt.OCF_READ_RSSI, bt.EVT_CMD_COMPLETE, 4, self.cmd_pkt)

            rssi = list(rssi)
            # rssi = struct.unpack('b', rssi[3])[0]
            return rssi
        except IOError:
            # Happens if connection fails (e.g. device is not in range)
            self.connected = False
            return None


b = BluetoothRSSI(addr='CC:21:19:CF:F9:F2')
status_history = []

while True:

    prox = b.get_rssi()[3]
    print('Proximity is {}'.format(str(prox)))
    prox = -prox if prox < 0 else prox + 0.1  # fix zero and negative problem
    print('Proximity adjusted is {}'.format(str(prox)))
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
