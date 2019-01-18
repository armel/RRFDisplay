#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
RRFTracker version Raspberry Pi 3B et Orange Pi Zero
Learn more about RRF on https://f5nlg.wordpress.com
Check video about RRFTracker on https://www.youtube.com/watch?v=rVW8xczVpEo
73 & 88 de F4HWN Armel
'''

import requests
import datetime
import time
import sys
import getopt
import os

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from luma.oled.device import ssd1306
from luma.core import legacy

from PIL import ImageFont

import config
from display import display_64

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

        return str(tmp[-3]), str(tmp[-2]), str(tmp[-1])

def main(argv):

    # Check and get arguments

    try:
        options, remainder=getopt.getopt(argv, '', ['help', 'i2c-port=', 'i2c-address=', 'display=', 'display-width=', 'display-height=', 'room='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in options:
        if opt == '--help':
            usage()
            sys.exit()
        elif opt in ('--i2c-port'):
            i2c_port = arg
        elif opt in ('--i2c-address'):
            i2c_address = int(arg, 16)
        elif opt in ('--display'):
            if arg not in ['sh1106', 'ssd1306']:
                print 'Unknown display type (choose between \'sh1106\' and \'ssd1306\')'
                sys.exit()
            display = arg
        elif opt in ('--display-width'):
            display_width = int(arg)
        elif opt in ('--display-height'):
            display_height = int(arg)
        elif opt in ('--room'):
            if arg not in ['RRF', 'TEC', 'FON']:
                print 'Unknown room name (choose between \'RRF\', \'TEC\' and \'FON\')'
                sys.exit()
            room = arg

    # Boucle principale

    while(True):

        # If midnight...

        tmp = datetime.datetime.now()
        now = tmp.strftime('%H:%M:%S')
        hour = int(tmp.strftime('%H'))
        minute = int(now[3:-3])
        seconde = int(now[-2:])

        if(now[:5] == '00:00'):
            config.qso_total += qso
            config.qso = 0
            for q in xrange(0, 24):         # Clean histogram
                config.qso_hour[q] = 0

        # Request HTTP datas

        try:
            r = requests.get(url, verify=False, timeout=10)
            page = r.content
        except requests.exceptions.ConnectionError as errc:
            print ('Error Connecting:', errc)
        except requests.exceptions.Timeout as errt:
            print ('Timeout Error:', errt)

        search_start = page.find('transmitter":"')      # Search this pattern
        search_start += 14                              # Shift...
        search_stop = page.find('"', search_start)      # And close it...

        # If transmitter...

        if search_stop != search_start:

            if config.wake_up is False:            # Wake up screen...
                config.wake_up = wake_up_screen(config.device, config.wake_up)

            # Clean call

            tmp = page[search_start:search_stop]
            tmp = tmp.replace('(', '')
            tmp = tmp.replace(') ', ' ')

            config.call_current = tmp

            if (config.call_previous != config.call_current):
                config.call_previous = config.call_current

                for i in xrange(4, 0, -1):
                    config.call[i] = config.call[i - 1]
                    config.call_time[i] = config.call_time[i - 1]

                config.call[0] = config.call_current

                config.history = save_stat(config.history, config.call[1])
                config.qso += 1
            else:
                if (config.blanc is True):         # Stat (same call but new PTT...)
                    config.history = save_stat(config.history, config.call[0])

            config.blanc = False

            # Format call time

            tmp = datetime.datetime.now()
            now = tmp.strftime('%H:%M:%S')
            hour = int(tmp.strftime('%H'))

            config.qso_hour[hour] = connfig.qso - sum(config.qso_hour[:hour])

            config.call_time[0] = now

            config.line[0] = config.call[2]
            config.line[1] = config.call[1]
            config.line[2] = config.call[0]

        # If no Transmitter...

        else:
            if config.wake_up is True:             # Sleep screen...
                config.wake_up = wake_up_screen(config.device, config.wake_up)

            if config.blanc is False:
                config.blanc = True
                config.qso += 1

            config.line[0] = config.call[1]
            config.line[1] = config.call[0]
            if config.qso == 0:
                config.line[2] = config.call_time[0]
            else:
                config.line[2] = 'Last TX ' + config.call_time[0]

        if(config.blanc_alternate == 0):           # TX today
            tmp = 'TX Today '
            tmp += str(qso)

            config.line[4] = tmp

            config.blanc_alternate = 1

        elif(config.blanc_alternate == 1):         # Boot time
            tmp = 'Up '
            tmp += calc_uptime(time.time() - config.timestamp_start)

            config.line[4] = tmp

            blanc_alternate = 2

        elif(config.blanc_alternate == 2):         # TX total
            tmp = 'TX Total '
            tmp += str(qso_total + qso)

            config.line[4] = tmp

            config.blanc_alternate = 3

        elif(config.blanc_alternate == 3):         # Best link
            if len(config.history) >= 5:
                best = max(config.history, key=config.history.get)
                config.line[4] = best + ' ' + str(config.history[best]) + ' TX'
            else:
                config.line[4] = 'Need more datas'
        
            config.blanc_alternate = 0


        # Print screen

        font=ImageFont.truetype('fonts/7x5.ttf', 8)                           # Text font
        icon=ImageFont.truetype('fonts/fontello.ttf', 14)                     # Icon font

        with canvas(config.device) as draw:

            display_64()

        time.sleep(2)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
