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
from luma.oled.device import ssd1327

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
            s.i2c_port = int(arg)
        elif opt in ('--i2c-address'):
            s.i2c_address = int(arg, 16)
        elif opt in ('--display'):
            if arg not in ['sh1106', 'ssd1306', 'ssd1327']:
                print 'Unknown display type (choose between \'sh1106\', \'ssd1306\' and \'ssd1327\')'
                sys.exit()
            s.display = arg
        elif opt in ('--display-width'):
            s.display_width = int(arg)
        elif opt in ('--display-height'):
            s.display_height = int(arg)
        elif opt in ('--room'):
            if arg not in ['RRF', 'TECHNIQUE', 'INTERNATIONAL', 'LOCAL', 'BAVARDAGE', 'FON']:
                print 'Unknown room name (choose between \'RRF\', \'TECHNIQUE\', \'INTERNATIONAL\', \'LOCAL\', \'BAVARDAGE\' and \'FON\')'
                sys.exit()
            s.room_current = arg
        elif opt in ('--latitude'):
            s.latitude = float(arg)
        elif opt in ('--longitude'):
            s.longitude = float(arg)

    # Set serial
    serial = i2c(port=s.i2c_port, address=s.i2c_address)
    if s.display == 'sh1106':
        s.device = sh1106(serial, width=s.display_width, height=s.display_height, rotate=0)
    elif s.display == 'ssd1306':
        s.device = ssd1306(serial, width=s.display_width, height=s.display_height, rotate=0)
    elif s.display == 'ssd1327':
        s.device = ssd1327(serial, width=s.display_width, height=s.display_height, rotate=0, mode='RGB')


    url = s.room[s.room_current]['url']

    # Boucle principale
    s.timestamp_start = time.time()

    while(True):

        # Requete HTTP vers le flux json du salon produit par le RRFTracker 
        try:
            r = requests.get(url, verify=False, timeout=10)
        except requests.exceptions.ConnectionError as errc:
            print ('Error Connecting:', errc)
        except requests.exceptions.Timeout as errt:
            print ('Timeout Error:', errt)

        # Controle de la validité du flux json
        rrf_data = ''
        try:
            rrf_data = r.json()
        except:
            pass

        if rrf_data != '': # Si le flux est valide
            data_abstract = rrf_data['abstract'][0]
            data_activity = rrf_data['activity'][0]
            data_transmit = rrf_data['transmit'][0]
            data_last = rrf_data['last']
            data_elsewhere = rrf_data['elsewhere'][0]

            if data_transmit['Indicatif'] != '':
                if s.transmit is False:      # Wake up screen...
                    s.transmit = l.wake_up_screen(s.device, s.display, s.transmit)

                s.call_current = data_transmit['Indicatif']
                s.duration = data_transmit['TOT']

                s.message[0] = data_last[0]['Indicatif']
                s.message[1] = data_last[1]['Indicatif']
                s.message[2] = data_last[2]['Indicatif']

            else:
                if s.transmit is True:       # Sleep screen...
                    s.transmit = l.wake_up_screen(s.device, s.display, s.transmit)

                s.message[0] = data_last[0]['Indicatif']
                s.message[1] = data_last[1]['Indicatif']
                s.message[2] = 'Last TX ' + data_last[0]['Heure']

                if(s.blanc_alternate == 0):     # TX today
                    s.message[4] = 'TX Counter ' + data_abstract['TX total']
                    s.blanc_alternate = 1

                elif(s.blanc_alternate == 1):   # Boot time
                    s.message[4] = 'Up ' + l.calc_uptime(time.time() - s.timestamp_start)
                    s.blanc_alternate = 2

                elif(s.blanc_alternate == 2):   # Active node
                    s.message[4] = 'Active links ' + data_abstract['Links actifs']
                    s.blanc_alternate = 3

                elif(s.blanc_alternate == 3):   # Connected node
                    s.message[4] = 'Cnnected links ' + data_abstract['Links connectés']
                    s.blanc_alternate = 4
                    
                elif(s.blanc_alternate == 4):   # Total emission
                    s.message[4] = 'TX Duration ' + data_abstract['Emission cumulée']
                    s.blanc_alternate = 0

        print s.message

        exit()
        # Print screen
        if s.device.height == 128:
            d.display_128()
        elif s.device.height == 64:
            d.display_64()
        else:
            d.display_32()

        time.sleep(1)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
