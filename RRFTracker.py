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

from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from luma.oled.device import ssd1306

import config
import function
import display

def main(argv):

    # Check and get arguments

    try:
        options, remainder=getopt.getopt(argv, '', ['help', 'i2c-port=', 'i2c-address=', 'display=', 'display-width=', 'display-height=', 'room='])
    except getopt.GetoptError:
        function.usage()
        sys.exit(2)
    for opt, arg in options:
        if opt == '--help':
            function.usage()
            sys.exit()
        elif opt in ('--i2c-port'):
            config.i2c_port = arg
        elif opt in ('--i2c-address'):
            config.i2c_address = int(arg, 16)
        elif opt in ('--display'):
            if arg not in ['sh1106', 'ssd1306']:
                print 'Unknown display type (choose between \'sh1106\' and \'ssd1306\')'
                sys.exit()
            config.display = arg
        elif opt in ('--display-width'):
            config.display_width = int(arg)
        elif opt in ('--display-height'):
            config.display_height = int(arg)
        elif opt in ('--room'):
            if arg not in ['RRF', 'TEC', 'FON']:
                print 'Unknown room name (choose between \'RRF\', \'TEC\' and \'FON\')'
                sys.exit()
            config.room = arg

    # Set serial

    serial = i2c(port=config.i2c_port, address=config.i2c_address)
    if config.display == 'sh1106':
        config.device = sh1106(serial, width=config.display_width, height=config.display_height, rotate=0)
    else:
        config.device = ssd1306(serial, width=config.display_width, height=config.display_height, rotate=0)

    # Set url

    if config.room == 'RRF':
        url = 'http://rrf.f5nlg.ovh'
    elif config.room == 'TEC':
        url = 'http://rrf.f5nlg.ovh:82'
    elif config.room == 'FON':
        url = 'http://fon.f1tzo.com:81/'

    # Boucle principale

    config.timestamp_start = time.time()

    while(True):

        # If midnight...

        tmp = datetime.datetime.now()
        config.now = tmp.strftime('%H:%M:%S')
        config.hour = int(tmp.strftime('%H'))
        config.minute = int(config.now[3:-3])
        config.seconde = int(config.now[-2:])

        if(config.now[:5] == '00:00'):
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
                config.wake_up = function.wake_up_screen(config.device, config.wake_up)

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

                config.history = function.save_stat(config.history, config.call[1])
                config.qso += 1
            else:
                if (config.blanc is True):         # Stat (same call but new PTT...)
                    config.history = function.save_stat(config.history, config.call[0])

            config.blanc = False

            # Format call time

            tmp = datetime.datetime.now()
            config.now = tmp.strftime('%H:%M:%S')
            config.hour = int(tmp.strftime('%H'))

            config.qso_hour[config.hour] = config.qso - sum(config.qso_hour[:config.hour])

            config.call_time[0] = config.now

            config.line[0] = config.call[2]
            config.line[1] = config.call[1]
            config.line[2] = config.call[0]

        # If no Transmitter...

        else:
            if config.wake_up is True:             # Sleep screen...
                config.wake_up = function.wake_up_screen(config.device, config.wake_up)

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
            tmp += str(config.qso)

            config.line[4] = tmp

            config.blanc_alternate = 1

        elif(config.blanc_alternate == 1):         # Boot time
            tmp = 'Up '
            tmp += function.calc_uptime(time.time() - config.timestamp_start)

            config.line[4] = tmp

            config.blanc_alternate = 2

        elif(config.blanc_alternate == 2):         # TX total
            tmp = 'TX Total '
            tmp += str(config.qso_total + config.qso)

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

        if config.device.height == 64:
            display.display_64()
        else:
            display.display_32()

        time.sleep(2)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
