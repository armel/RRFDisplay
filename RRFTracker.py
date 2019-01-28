#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
RRFTracker version Raspberry Pi 3B et Orange Pi Zero
Learn more about RRF on https://f5nlg.wordpress.com
Check video about RRFTracker on https://www.youtube.com/watch?v=rVW8xczVpEo
73 & 88 de F4HWN Armel
'''

import settings as s
import display as d
import lib as l

import requests
import datetime
import time
import sys
import getopt

from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from luma.oled.device import ssd1306


def main(argv):

    # Check and get arguments
    try:
        options, remainder = getopt.getopt(argv, '', ['help', 'i2c-port=', 'i2c-address=', 'display=', 'display-width=', 'display-height=', 'room=', 'latitude=', 'longitude='])
    except getopt.GetoptError:
        l.usage()
        sys.exit(2)
    for opt, arg in options:
        if opt == '--help':
            l.usage()
            sys.exit()
        elif opt in ('--i2c-port'):
            s.i2c_port = arg
        elif opt in ('--i2c-address'):
            s.i2c_address = int(arg, 16)
        elif opt in ('--display'):
            if arg not in ['sh1106', 'ssd1306']:
                print 'Unknown display type (choose between \'sh1106\' and \'ssd1306\')'
                sys.exit()
            s.display = arg
        elif opt in ('--display-width'):
            s.display_width = int(arg)
        elif opt in ('--display-height'):
            s.display_height = int(arg)
        elif opt in ('--room'):
            if arg not in ['RRF', 'TEC', 'FON']:
                print 'Unknown room name (choose between \'RRF\', \'TEC\' and \'FON\')'
                sys.exit()
            s.room = arg
        elif opt in ('--latitude'):
            s.latitude = float(arg)
        elif opt in ('--longitude'):
            s.longitude = float(arg)

    # Set serial
    serial = i2c(port=s.i2c_port, address=s.i2c_address)
    if s.display == 'sh1106':
        s.device = sh1106(serial, width=s.display_width, height=s.display_height, rotate=0)
    else:
        s.device = ssd1306(serial, width=s.display_width, height=s.display_height, rotate=0)

    # Set url
    if s.room == 'RRF':
        url = 'http://rrf.f5nlg.ovh'
    elif s.room == 'TEC':
        url = 'http://rrf.f5nlg.ovh:82'
    elif s.room == 'FON':
        url = 'http://fon.f1tzo.com:81/'

    # Boucle principale
    s.timestamp_start = time.time()

    while(True):

        # If midnight...
        tmp = datetime.datetime.now()
        s.now = tmp.strftime('%H:%M:%S')
        s.hour = int(tmp.strftime('%H'))
        s.minute = int(s.now[3:-3])
        s.seconde = int(s.now[-2:])

        if(s.now[:5] == '00:00'):
            s.qso_total += s.qso
            s.qso = 0
            for q in xrange(0, 24):         # Clean histogram
                s.qso_hour[q] = 0

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

            if s.wake_up is False:      # Wake up screen...
                s.wake_up = l.wake_up_screen(s.device, s.display, s.wake_up)

            # Clean call
            tmp = page[search_start:search_stop]
            tmp = tmp.replace('(', '')
            tmp = tmp.replace(') ', ' ')
            tmp = tmp.replace('\u0026U', '&')   # Replace ampersand...

            s.call_current = tmp

            if (s.call_previous != s.call_current):
                s.tot_start = time.time()
                s.tot_current = s.tot_start
                s.call_previous = s.call_current

                for i in xrange(4, 0, -1):
                    s.call[i] = s.call[i - 1]
                    s.call_time[i] = s.call_time[i - 1]

                s.call[0] = s.call_current

                s.history = l.save_stat(s.history, s.call[1])
                s.qso += 1
            else:
                if s.tot_start is '':
                    s.tot_start = time.time()
                s.tot_current = time.time()
                if (s.blanc is True):         # Stat (same call but new PTT...)
                    s.history = l.save_stat(s.history, s.call[0])

            s.blanc = False

            # Format call time
            tmp = datetime.datetime.now()
            s.now = tmp.strftime('%H:%M:%S')
            s.hour = int(tmp.strftime('%H'))

            s.qso_hour[s.hour] = s.qso - sum(s.qso_hour[:s.hour])

            s.call_time[0] = s.now

            s.message[0] = s.call[2]
            s.message[1] = s.call[1]
            s.message[2] = s.call[0]

        # If no Transmitter...
        else:
            if s.wake_up is True:       # Sleep screen...
                s.wake_up = l.wake_up_screen(s.device, s.display, s.wake_up)

            if s.blanc is False:
                s.blanc = True
                duration = int(s.tot_current) - int(s.tot_start)
                s.tot_current = ''
                s.tot_start = ''
                if duration > 3:
                    s.qso += 1

            s.message[0] = s.call[1]
            s.message[1] = s.call[0]
            if s.qso == 0:
                s.message[2] = s.call_time[0]
            else:
                s.message[2] = 'Last TX ' + s.call_time[0]

        if(s.blanc_alternate == 0):     # TX today
            tmp = 'TX Today '
            tmp += str(s.qso)

            s.message[4] = tmp

            s.blanc_alternate = 1

        elif(s.blanc_alternate == 1):   # Boot time
            tmp = 'Up '
            tmp += l.calc_uptime(time.time() - s.timestamp_start)

            s.message[4] = tmp

            s.blanc_alternate = 2

        elif(s.blanc_alternate == 2):   # TX total
            tmp = 'TX Total '
            tmp += str(s.qso_total + s.qso)

            s.message[4] = tmp

            s.blanc_alternate = 3

        elif(s.blanc_alternate == 3):   # Best link
            if len(s.history) >= 5:
                best = max(s.history, key=s.history.get)
                s.message[4] = best + ' ' + str(s.history[best]) + ' TX'
            else:
                s.message[4] = 'Need more datas'

            s.blanc_alternate = 0

        # Print screen
        if s.device.height == 64:
            d.display_64()
        else:
            d.display_32()

        time.sleep(2)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
