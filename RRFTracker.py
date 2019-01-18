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

    # Default i2c_port and i2c_address

    i2c_port = 0                            # Default value ! Check port with i2cdetect...
    i2c_address = 0x3C                      # Default value ! Check address with i2cdetect...
    display = 'sh1106'                      # Default value !
    display_width = 128                     # Default value !
    display_height = 64                     # Default value !
    room = 'RRF'                            # Default value !

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

    # Set constants & variables

    SMALL_BITMAP_FONT = [
        [0x1f, 0x11, 0x1f, 0x00],           # 0
        [0x00, 0x1f, 0x00, 0x00],           # 1
        [0x1d, 0x15, 0x17, 0x00],           # 2
        [0x11, 0x15, 0x1f, 0x00],           # 3
        [0x07, 0x08, 0x1c, 0x00],           # 4
        [0x17, 0x15, 0x1d, 0x00],           # 5
        [0x1f, 0x15, 0x1d, 0x00],           # 6
        [0x11, 0x09, 0x07, 0x00],           # 7
        [0x1f, 0x15, 0x1f, 0x00],           # 8
        [0x17, 0x15, 0x1f, 0x00],           # 9
        [0x00, 0x1b, 0x00, 0x00],           # :
        [0x1f, 0x05, 0x1a, 0x00],           # R
        [0x1f, 0x05, 0x01, 0x00],           # F
        [0x1f, 0x11, 0x1f, 0x00],           # O
        [0x01, 0x1f, 0x01, 0x00],           # T
        [0x1f, 0x02, 0x04, 0x1f],           # N
        [0x1f, 0x11, 0x11, 0x00],           # C
        [0x1f, 0x15, 0x11, 0x00]            # E
    ]

    letter = {'C': 16, 'E': 17, 'F': 12, 'N': 15, 'O': 13, 'R': 11, 'T': 14}

    call = ['F4HWN', 'RRFTracker', '', '', '']
    call_current = call[0]
    call_previous = call[1]
    call_time = ['Waiting TX', '', '', '', '']

    blanc = True
    blanc_alternate = 0

    qso = 0
    qso_total = 0
    qso_hour = [0] * 24

    wake_up = True
    extended = False

    history = dict()
    line = [None] * 7

    # Set serial

    serial = i2c(port=i2c_port, address=i2c_address)
    if display == 'sh1106':
        device = sh1106(serial, width=display_width, height=display_height, rotate=0)
    else:
        device = ssd1306(serial, width=display_width, height=display_height, rotate=0)

    # Set url

    if room == 'RRF':
        url = 'http://rrf.f5nlg.ovh'
    elif room == 'TEC':
        url = 'http://rrf.f5nlg.ovh:82'
    elif room == 'FON':
        url = 'http://fon.f1tzo.com:81/'

    # Set date

    timestamp_start = time.time()

    # Check board

    tmp = os.popen('uname -a').readline()
    if 'sun8i' in tmp:
        board = 'Orange Pi'
    else:
        board = 'Raspberry Pi'

    # Boucle principale

    while(True):

        # If midnight...

        tmp = datetime.datetime.now()
        now = tmp.strftime('%H:%M:%S')
        hour = int(tmp.strftime('%H'))
        minute = int(now[3:-3])
        seconde = int(now[-2:])

        if(now[:5] == '00:00'):
            qso_total += qso
            qso = 0
            for q in xrange(0, 24):         # Clean histogram
                qso_hour[q] = 0

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

            if wake_up is False:            # Wake up screen...
                wake_up = wake_up_screen(device, wake_up)

            # Clean call

            tmp = page[search_start:search_stop]
            tmp = tmp.replace('(', '')
            tmp = tmp.replace(') ', ' ')

            call_current = tmp

            if (call_previous != call_current):
                call_previous = call_current

                for i in xrange(4, 0, -1):
                    call[i] = call[i - 1]
                    call_time[i] = call_time[i - 1]

                call[0] = call_current

                history = save_stat(history, call[1])
                qso += 1
            else:
                if (blanc is True):         # Stat (same call but new PTT...)
                    history = save_stat(history, call[0])

            blanc = False

            # Format call time

            tmp = datetime.datetime.now()
            now = tmp.strftime('%H:%M:%S')
            hour = int(tmp.strftime('%H'))

            qso_hour[hour] = qso - sum(qso_hour[:hour])

            call_time[0] = now

            line[0] = call[2]
            line[1] = call[1]
            line[2] = call[0]

        # If no Transmitter...

        else:
            if wake_up is True:             # Sleep screen...
                wake_up = wake_up_screen(device, wake_up)

            if blanc is False:
                blanc = True
                qso += 1

            line[0] = call[1]
            line[1] = call[0]
            if qso == 0:
                line[2] = call_time[0]
            else:
                line[2] = 'Last TX ' + call_time[0]

        if(blanc_alternate == 0):           # TX today
            tmp = 'TX Today '
            tmp += str(qso)

            line[4] = tmp

            blanc_alternate = 1

        elif(blanc_alternate == 1):         # Boot time
            tmp = 'Up '
            tmp += calc_uptime(time.time() - timestamp_start)

            line[4] = tmp

            blanc_alternate = 2

        elif(blanc_alternate == 2):         # TX total
            tmp = 'TX Total '
            tmp += str(qso_total + qso)

            line[4] = tmp

            blanc_alternate = 3

        elif(blanc_alternate == 3):         # Best link
            if len(history) >= 5:
                best = max(history, key=history.get)
                line[4] = best + ' ' + str(history[best]) + ' TX'
            else:
                line[4] = 'Need more datas'
        
            blanc_alternate = 0


        # Print screen

        font=ImageFont.truetype('fonts/7x5.ttf', 8)                           # Text font
        icon=ImageFont.truetype('fonts/fontello.ttf', 14)                     # Icon font

        with canvas(device) as draw:

            display_64()

        time.sleep(2)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
