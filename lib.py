#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
RRFTracker version Raspberry Pi 3B et Orange Pi Zero
Learn more about RRF on https://f5nlg.wordpress.com
Check video about RRFTracker on https://www.youtube.com/watch?v=rVW8xczVpEo
73 & 88 de F4HWN Armel
'''

import os


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
    print '  --display          set display (default=sh1106, choose between [sh1106, ssd1306])'
    print '  --display-width    set display width (default=128)'
    print '  --display-height   set display height (default=64)'
    print
    print 'Room settings:'
    print '  --room ROOM        set room (default=RRF, choose between [RRF, TEC, FON])'
    print
    print '73 from F4HWN Armel'


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
def wake_up_screen(device, wake_up):
    if wake_up is True:
        for i in xrange(225, 32, -1):
            device.contrast(i)         # No Transmitter
        return False
    else:
        for i in xrange(32, 225):
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
        mem_total = int(tmp[1][:-1])
        mem_use = int(tmp[2][:-1])

        return str(int((float(mem_use) / float(mem_total)) * 100)), str(mem)

    elif value == 'disk':
        tmp = list(os.popen('df -h'))
        tmp = tmp[1].strip()
        tmp = tmp.split()

        disk = tmp[1]
        disk_total = (tmp[1][:-1]).replace(',', '.')
        disk_use = (tmp[2][:-1]).replace(',', '.')

        return str(int((float(disk_use) / float(disk_total)) * 100)), str(disk)

    elif value == 'load':
        tmp = list(os.popen('w | head -n 1'))
        tmp = tmp[0].strip()
        tmp = tmp.split()

        return str(tmp[-3]) + ' ' + str(tmp[-2]) + ' ' + str(tmp[-1])

    elif value == 'up':
        tmp = list(os.popen('w | head -n 1'))
        tmp = tmp[0].strip()
        tmp = tmp.split()

        if len(tmp) == 7:
            return tmp[1] + ' d' + ', ' + tmp[3] + ':' + tmp[5]
        elif len(tmp) == 5:
            return tmp[1] + ' h' + ', ' + tmp[3]
        else:
            return tmp[1] + ' m' 

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
