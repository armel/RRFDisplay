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

    call = ['F4HWN', 'RRFTracker', '', '', '', '', '', '', '', '']
    call_current = call[0]
    call_previous = call[1]
    call_time = ['Waiting TX', '', '', '', '', '', '', '', '', '']

    blanc = True
    blanc_alternate = 0

    qso = 0
    qso_total = 0
    qso_hour = [0] * 24

    wake_up = True
    extended = False

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

    history = dict()

    line = [None] * 7

    # Check board

    tmp = os.popen('uname -a').readline()
    if 'sun8i' in tmp:
        board = 'orangepi'
    else:
        board = 'raspi'

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

                for i in xrange(9, 0, -1):
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
            if len(history) > 4:
                best = max(history, key=history.get)
                line[4] = best + ' ' + str(history[best]) + ' TX'
            else:
                line[4] = 'Need more datas'

            blanc_alternate = 4

        elif(blanc_alternate == 4):         # Thermal monitor
            line[4] = 'Temp ' + system_info('temp') + ' C'

            blanc_alternate = 5

        elif(blanc_alternate == 5):         # Freq monitor
            line[4] = 'Freq ' + system_info('freq') + ' MHz'

            blanc_alternate = 6

        elif(blanc_alternate == 6):         # Mem monitor
            percent, mem = system_info('mem')
            line[4] = 'Mem ' + percent + ' % of ' + mem

            blanc_alternate = 7

        elif(blanc_alternate == 7):         # Disk monitor
            percent, disk = system_info('disk')
            line[4] = 'Disk ' + percent + ' % of ' + disk

            blanc_alternate = 0


        # Print screen

        font=ImageFont.truetype('fonts/7x5.ttf', 8)                           # Text font
        icon=ImageFont.truetype('fonts/fontello.ttf', 14)                     # Icon font

        with canvas(device) as draw:

            if extended is False:

                if 'Waiting TX' not in call_time and len(history) >= 5 and device.height == 64:
                    extended = True

            if wake_up is False and extended is True and minute % 4 == 0:       # History log extended

                draw.rectangle((0, 0, 127, 63), fill='black')

                for i in xrange(0, 128, 2):
                    draw.point((i, 10), fill='white')

                w, h = draw.textsize(text=room + ' Last TX', font=font)
                tab = (device.width - w) / 2
                draw.text((tab, 0), room + ' Last TX', font=font, fill='white')

                i = 16

                for j in xrange(0, 5):
                    draw.rectangle((0, i - 1, 42, i + 7), fill='white')
                    draw.line((43, i, 43, i + 6), fill='white')
                    draw.line((44, i + 2, 44, i + 4), fill='white')
                    draw.point((45, i + 3), fill='white')

                    draw.text((1, i), call_time[j], font=font, fill='black')
                    draw.text((54, i), call[j], font=font, fill='white')

                    i += 10

            elif wake_up is False and extended is True and minute % 2 == 0:     # Best log extended

                draw.rectangle((0, 0, 127, 63), fill='black')
                for i in xrange(0, 128, 2):
                    draw.point((i, 10), fill='white')

                w, h = draw.textsize(text=room + ' Best TX', font=font)
                tab = (device.width - w) / 2
                draw.text((tab, 0), room + ' Best TX', font=font, fill='white')

                tmp = sorted(history.items(), key=lambda x: x[1])
                tmp.reverse()

                best_min = min(history, key=history.get)
                best_max = max(history, key=history.get)

                i = 16

                for j in xrange(0, 5):
                    c, n = tmp[j]
                    t = interpolation(n, history[best_min], history[best_max], 12, 42)
                    n = str(n)

                    draw.rectangle((0, i - 1, t, i + 7), fill='white')
                    draw.line((t + 1, i, t + 1, i + 6), fill='white')
                    draw.line((t + 2, i + 2, t + 2, i + 4), fill='white')
                    draw.point((t + 3, i + 3), fill='white')

                    draw.text((1, i), n, font=font, fill='black')
                    draw.text((54, i), c, font=font, fill='white')

                    i += 10

            else:                                                               # If not extended

                if device.height == 64:     # Only if 128 x 64 pixels
                    for i in xrange(0, 128, 2):
                        draw.point((i, 25), fill='white')
                        draw.point((i, 40), fill='white')
                        draw.text((0, 26), u'\ue801', font=icon, fill='white')  # Icon stat

                if wake_up is True:
                    draw.text((2, 0), u'\uf130', font=icon, fill='white')       # Icon talk

                if line[2][:4] == 'Last':                                       # Icon clock (DIY...)
                    x = 6
                    y = 17
                    draw.ellipse((x - 6, y - 6, x + 6, y + 6), outline='white')
                    draw.line((x, y, x + 2, y + 2), fill='white')
                    draw.line((x, y, x, y - 3), fill='white')

                # Print data

                i = 0

                for l in line:
                    if l is not None:
                        w, h = draw.textsize(text=l, font=font)
                        tab = (device.width - w) / 2
                        vide = ' ' * 22             # Hack to speed clear screen line...
                        draw.text((0, i), vide, font=font, fill='white')
                        draw.text((tab, i), l, font=font, fill='white')
                        i += h
                        if i == 24:
                            if device.height != 64:  # Break if 128 x 32 pixels
                                break
                            i += 6

                # Draw stats histogram

                if device.height == 64:              # Only if 128 x 64 pixels

                    qso_hour_max = max(qso_hour)

                    i = 4

                    for q in qso_hour:
                        if q != 0:
                            h = interpolation(q, 1, qso_hour_max, 1, 15)
                        else:
                            h = 0
                        draw.rectangle((0 + i, 57, i + 2, (57 - 15)), fill='black')
                        draw.rectangle((0 + i, 57, i + 2, (57 - h)), fill='white')
                        i += 5

                    legacy.text(draw,   (4, 59), chr(0) + chr(0), fill='white', font=SMALL_BITMAP_FONT)
                    legacy.text(draw,  (32, 59), chr(0) + chr(6), fill='white', font=SMALL_BITMAP_FONT)
                    legacy.text(draw,  (62, 59), chr(1) + chr(2), fill='white', font=SMALL_BITMAP_FONT)
                    legacy.text(draw,  (92, 59), chr(1) + chr(8), fill='white', font=SMALL_BITMAP_FONT)
                    legacy.text(draw, (115, 59), chr(2) + chr(3), fill='white', font=SMALL_BITMAP_FONT)

            if blanc_alternate == 4:
                # Print Room

                i = 115

                for c in room:
                    legacy.text(draw,  (i, 1), chr(letter[c]), fill='white', font=SMALL_BITMAP_FONT)
                    i += 4
            else:
                # Print Clock

                i = 108

                for c in now:
                    if c == ':':
                        c = 10
                    else:
                        c = int(c)
                    legacy.text(draw,  (i, 1), chr(c), fill='white', font=SMALL_BITMAP_FONT)
                    i += 4

        time.sleep(2)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
