#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
RRFTracker version Raspberry Pi 3B et Orange Pi Zero
Learn more about RRF on https://f5nlg.wordpress.com
Check video about RRFTracker on https://www.youtube.com/watch?v=rVW8xczVpEo
73 & 88 de F4HWN Armel
'''

import os
from math import cos, asin, sqrt, ceil


# Usage
def usage():
    print 'Usage: RRFTracker.py [options ...]'
    print
    print '--help               this help'
    print
    print 'I2C settings:'
    print '  --i2c-port         set i2c port (default=0)'
    print '  --i2c-address      set i2c address (default=0x3C)'
    print
    print 'Display settings:'
    print '  --display          set display (default=sh1106, choose between [sh1106, ssd1306, ssd1327])'
    print '  --display-width    set display width (default=128)'
    print '  --display-height   set display height (default=64)'
    print
    print 'Room settings:'
    print '  --room ROOM        set room (default=RRF, choose between [RRF, TEC, FON])'
    print
    print 'WGS84 settings:'
    print '  --latitude         set latitude (default=48.8483808, format WGS84)'
    print '  --longitude        set longitude (default=2.2704347, format WGS84)'
    print
    print '88 & 73 from F4HWN Armel'


# Calculate uptime with a microtime
def calc_uptime(n):
    n = int(n)
    day = n / (24 * 3600)
    n = n % (24 * 3600)
    hour = n / 3600
    n %= 3600
    minute = n / 60

    tmp = ''

    if day < 10:
        tmp += '0'
    tmp += str(day)
    tmp += ' d, '

    if hour < 10:
        tmp += '0'
    tmp += str(hour)

    tmp += ':'

    if minute < 10:
        tmp += '0'
    tmp += str(minute)

    return tmp


# Save stats to get most active link
def save_stat(history, call):
    if call in history:
        history[call] += 1
    else:
        history[call] = 1

    return history


# Wake up screen
def wake_up_screen(device, display, wake_up):
    if 'sh1106' in display:
        sleep_level = 32
    elif 'ssd1306' in display:
        sleep_level = 32
    else:
        sleep_level = 32

    if wake_up is True:
        for i in xrange(225, sleep_level, -1):
            device.contrast(i)         # No Transmitter
        return False
    else:
        for i in xrange(sleep_level, 225):
            device.contrast(i)         # Transmitter
        return True


# Calc interpolation
def interpolation(value, in_min, in_max, out_min, out_max):
    if (in_max - in_min) != 0:
        return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)
    else:
        return 0


# Get system info
def system_info(value):

    if value == 'temp':
        tmp = int(os.popen('cat /sys/class/thermal/thermal_zone0/temp').readline())
        if tmp > 1000:
            tmp /= 1000

        return str(tmp)

    elif value == 'freq':
        tmp = int(os.popen('cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq').readline())
        if tmp > 1000:
            tmp /= 1000

        return str(tmp)

    elif value == 'mem':
        tmp = list(os.popen('free -h'))
        tmp = tmp[1].strip()
        tmp = tmp.split()

        mem = tmp[1]
        #mem_total = int(tmp[1][:-1])
        #mem_use = int(tmp[2][:-1])

        mem_total = int(tmp[1][:-2])
        mem_use = int(tmp[2][:-2])

        return str(int((float(mem_use) / float(mem_total)) * 100)), str(mem)

    elif value == 'disk':
        tmp = list(os.popen('df -h'))
        tmp = tmp[1].strip()
        tmp = tmp.split()

        disk = tmp[1]
        #disk_total = (tmp[1][:-1]).replace(',', '.')
        #disk_use = (tmp[2][:-1]).replace(',', '.')
        disk_total = (tmp[1][:-2]).replace(',', '.')
        disk_use = (tmp[2][:-2]).replace(',', '.')

        #return str(int((float(disk_use) / float(disk_total)) * 100)), str(disk)
        return "FixMe"

    elif value == 'load':
        tmp = list(os.popen('w | head -n 1'))
        tmp = tmp[0].strip()
        tmp = tmp.split()

        return str(tmp[-3]) + ' ' + str(tmp[-2]) + ' ' + str(tmp[-1])

    elif value == 'up':
        tmp = list(os.popen('uptime -p'))
        tmp = tmp[0].strip()
        tmp = [int(s) for s in tmp.split() if s.isdigit()]

        if len(tmp) == 3:
            day = tmp[0]
            hour = tmp[1]
            minute = tmp[2]
        elif len(tmp) == 2:
            day = 0
            hour = tmp[0]
            minute = tmp[1]
        else:
            day = 0
            hour = 0
            minute = tmp[0]

        tmp = ''

        if day < 10:
            tmp += '0'
        tmp += str(day)
        tmp += ' d, '

        if hour < 10:
            tmp += '0'
        tmp += str(hour)

        tmp += ':'

        if minute < 10:
            tmp += '0'
        tmp += str(minute)

        return str(tmp)

    elif value == 'ip':
        tmp = list(os.popen('hostname -I'))
        tmp = tmp[0].strip()

        return str(tmp)

    elif value == 'arch':
        tmp = os.popen('uname -a').readline()
        if 'sun8i' in tmp:
            tmp = 'Orange Pi'
        else:
            tmp = 'Raspberry Pi'

        return str(tmp)


# Compute distance
def calc_distance(call, latitude_1, longitude_1):
    data = [line.strip() for line in open('data/wgs84.dat')]

    for line in data:
        tmp = line.split(' ')
        if tmp[0] in call:
            latitude_2 = float(tmp[1])
            longitude_2 = float(tmp[2])
            p = 0.017453292519943295        # Approximation Pi/180
            a = 0.5 - cos((latitude_2 - latitude_1) * p) / 2 + cos(latitude_1 * p) * cos(latitude_2 * p) * (1 - cos((longitude_2 - longitude_1) * p)) / 2
            r = (12742 * asin(sqrt(a)))
            if r < 100:
                r = round((12742 * asin(sqrt(a))), 1)
            else:
                r = int(ceil(12742 * asin(sqrt(a))))
            return r
    return 0
