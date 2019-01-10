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
import sys, getopt
import os
import re

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.oled.device import sh1106
from luma.oled.device import ssd1306
from luma.core import legacy

from PIL import ImageFont

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
    if wake_up == True:
        for i in xrange(255, 32, -1):
            device.contrast(i)         # No Transmitter
        return False
    else:
        for i in xrange(32, 255):
            device.contrast(i)         # Transmitter
        return True


# Calc interpolation

def interpolation(value, in_min, in_max, out_min, out_max):
    if (in_max - in_min) != 0:
        return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)
    else:
        return 0


def main(argv):

    # Default i2c_port and i2c_address

    i2c_port = 0                            # Default value ! Check port with i2cdetect...
    i2c_address = 0x3C                      # Default value ! Check adress with i2cdetect...
    display = 'sh1106'                      # Default value !

    # Check and get arguments

    try:
        options, remainder = getopt.getopt(argv, 'hp:a:d:', ['i2c-port=','i2c-address=', 'display='])
    except getopt.GetoptError:
        print 'usage: RRFTracker.py -p <i2c_port> -a <i2c_address>'
        sys.exit(2)
    for opt, arg in options:
        if opt == '-h':
            print 'usage: RRFTracker.py'
            print '-h, --help'
            print '-p, --i2c-port I2C_PORT'
            print '-a, --i2c-address I2C_ADDRESS'
            print '-d, --display DISPLAY (choose from \'sh1106\', \'ssd1306\')'
            sys.exit()
        elif opt in ('-p', '--i2c-port'):
            i2c_port = arg
        elif opt in ('-a', '--i2c-address'):
            i2c_address = int(arg, 16)
        elif opt in ('-d', '--display'):
            if arg not in ['sh1106', 'ssd1306']:
                print 'Unknown display type (choose between \'sh1106\' and \'ssd1306\')'
                sys.exit()
            display = arg

    # Set constants & variables

    url = 'http://rrf.f5nlg.ovh/'

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
        [0x00, 0x1b, 0x00, 0x00]            # :
    ]

    call = ['F4HWN', 'RRFTracker', '']
    call_current = call[0]
    call_previous = call[1]
    call_time = 'Waiting TX'

    blanc = True
    blanc_alternate = 0

    qso = 0
    qso_total = 0
    qso_hour = [0] * 24

    wake_up = True

    # Set serial

    serial = i2c(port = i2c_port, address = i2c_address)
    if display == 'sh1106':                 # 128 x 64 pixels
        device = sh1106(serial, width = 128, height = 64, rotate = 0)
    else:                                   # 128 x 32 pixels
        device = ssd1306(serial, width = 128, height = 32, rotate = 0)

    # Set date

    timestamp_start = time.time()

    history = dict()
    line = [None] * 7

    # Check board

    tmp = os.popen("uname -a").readline()
    if tmp.find('sun8i'):
        board = 'orangepi'
    else:
        board = 'raspi'

    # Boucle principale

    while(True):

        # If midnight...

        tmp = datetime.datetime.now()
        now = tmp.strftime('%H:%M')
        hour = int(tmp.strftime('%H'))

        if(now == '00:00'):
            qso_total += qso
            qso = 0
            for q in xrange(0, 24):         # Clean histogram
                qso_hour[q] = 0

        # Request HTTP datas

        try:
            r = requests.get(url, verify = False, timeout = 10)
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
                call[2] = call[1]
                call[1] = call[0]
                call[0] = call_current
                history = save_stat(history, call[1])
                qso += 1
            else:
                if (blanc is True):         # Stat (same call but new PTT...)
                    history = save_stat(history, call[0])

            blanc = False

            # Format call time

            call_time = 'Last TX '
            tmp = datetime.datetime.now()
            now = tmp.strftime('%H:%M:%S')
            hour = int(tmp.strftime('%H'))

            qso_hour[hour] = qso - sum(qso_hour[:hour])

            call_time += now

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
            line[2] = call_time

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
                line[4] = best + ' - ' + str(history[best]) + ' TX'
            else:
                line[4] = 'Need more datas'

            blanc_alternate = 4

        elif(blanc_alternate == 4):         # Thermal monitor
            if board == 'orangepi':
                tmp = os.popen("cat /sys/devices/virtual/thermal/thermal_zone0/temp").readline()
                tmp = int(tmp)
            else:
                tmp = os.popen("vcgencmd measure_temp").readline()
                tmp = re.findall('\d+\.\d+', tmp)
                tmp = tmp[0]

            line[4] = 'Spotnik Temp ' + str(tmp) + ' C'

            blanc_alternate = 0


        # Print screen

        font = ImageFont.truetype('fonts/7x5.ttf', 8)                           # Text font
        icon = ImageFont.truetype('fonts/fontello.ttf', 14)                     # Icon font
                  
        with canvas(device) as draw:
            if device.height == 64:     # Only if 128 x 64 pixels
                for i in xrange(0, 128, 2):
                    draw.point((i, 25), fill = 'white')
                    draw.point((i, 40), fill = 'white')
                    draw.text((0,26), u"\ue801", font = icon, fill = 'white')   # Icon stat

            
            if wake_up is True:
                draw.text((2, 0), u"\uf130", font = icon, fill = 'white')       # Icon talk
            
            if line[2][:4] == 'Last':                                           # Icon clock (DIY...)
                x = 6
                y = 17
                draw.ellipse((x - 6, y - 6, x + 6, y + 6), outline = 'white')
                draw.line((x, y, x + 2, y + 2), fill = 'white')
                draw.line((x, y, x, y - 3), fill = 'white')

            # Print data

            i = 0

            for l in line:
                if l is not None:
                    w, h = draw.textsize(text = l, font = font)
                    tab = (device.width - w) / 2
                    vide = ' ' * 22             # Hack to speed clear screen line... 
                    draw.text((0, i), vide, font = font, fill = 'white')
                    draw.text((tab, i), l, font = font, fill = 'white')
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
                    draw.rectangle((0 + i, 57, i + 2, (57 - 15)), fill = 'black')
                    draw.rectangle((0 + i, 57, i + 2, (57 - h)), fill = 'white')
                    i += 5

                legacy.text(draw,   (4, 59), chr(0) + chr(0), fill = 'white', font=SMALL_BITMAP_FONT)
                legacy.text(draw,  (32, 59), chr(0) + chr(6), fill = 'white', font=SMALL_BITMAP_FONT)
                legacy.text(draw,  (62, 59), chr(1) + chr(2), fill = 'white', font=SMALL_BITMAP_FONT)
                legacy.text(draw,  (92, 59), chr(1) + chr(8), fill = 'white', font=SMALL_BITMAP_FONT)
                legacy.text(draw, (115, 59), chr(2) + chr(3), fill = 'white', font=SMALL_BITMAP_FONT)

            # Draw clock

            i = 108

            for c in now:
                if c == ':':
                    c = 10
                else:
                    c = int(c)
                legacy.text(draw,  (i, 0), chr(c), fill = 'white', font=SMALL_BITMAP_FONT)
                i += 4

        time.sleep(2)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
