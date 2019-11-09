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
        tmp = datetime.datetime.now()
        s.day = tmp.strftime('%Y-%m-%d')
        s.now = tmp.strftime('%H:%M:%S')
        s.hour = int(tmp.strftime('%H'))
        s.minute = int(s.now[3:-3])
        s.seconde = int(s.now[-2:])

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
            data_activity = rrf_data['activity']
            data_transmit = rrf_data['transmit'][0]
            data_last = rrf_data['last']
            data_all = rrf_data['allExtended']
            data_elsewhere = rrf_data['elsewhere'][0]

            for q in xrange(0, 24):         # Load histogram
                s.qso_hour[q] = data_activity[q][u'TX']

            if len(rrf_data['last']) >= 10:
                limit = 10
            else:
                limit = len(rrf_data['last'])

            for q in xrange(0, limit):
                s.call[q] = l.sanitize_call(rrf_data['last'][q][u'Indicatif'].encode('utf-8'))
                s.call_time[q] = rrf_data['last'][q][u'Heure']

            if len(rrf_data['allExtended']) >= 10:
                limit = 10
            else:
                limit = len(rrf_data['allExtended'])

            for q in xrange(0, limit):
                s.best[q] = l.sanitize_call(rrf_data['allExtended'][q][u'Indicatif'].encode('utf-8'))
                s.best_time[q] = l.convert_time_to_second(rrf_data['allExtended'][q][u'Durée'])

            s.message[0] = l.sanitize_call(data_last[2][u'Indicatif'].encode('utf-8'))
            s.message[1] = l.sanitize_call(data_last[1][u'Indicatif'].encode('utf-8'))
            s.message[2] = l.sanitize_call(data_last[0][u'Indicatif'].encode('utf-8'))

            i = 0
            for data in rrf_data['elsewhere'][6]:
                if data in ['RRF', 'TECHNIQUE', 'INTERNATIONAL', 'LOCAL', 'BAVARDAGE', 'FON']:
                    tmp = rrf_data['elsewhere'][6][data]
                    if tmp != 0:
                        color = 'white'
                    else:
                        color = 'blue'

                    s.message[5 + i] = data[:3] + '  ' + rrf_data['elsewhere'][3][data] + ' ' + rrf_data['elsewhere'][5][data]
                    i += 1

            for m in s.message:
                print m

            if data_transmit['Indicatif'] != '':
                if s.transmit is False:      # Wake up screen...
                    s.transmit = l.wake_up_screen(s.device, s.display, s.transmit)

                s.call_current = l.sanitize_call(data_transmit[u'Indicatif'].encode('utf-8'))

                s.duration = data_transmit[u'TOT']

            else:
                if s.transmit is True:       # Sleep screen...
                    s.transmit = l.wake_up_screen(s.device, s.display, s.transmit)

            if(s.blanc_alternate == 0):     # TX today
                s.message[4] = 'Total TX ' + str(data_abstract[u'TX total'])
                s.blanc_alternate = 1

            elif(s.blanc_alternate == 1):   # Boot time
                s.message[4] = 'Up ' + l.calc_uptime(time.time() - s.timestamp_start)
                s.blanc_alternate = 2

            elif(s.blanc_alternate == 2):   # Active node
                s.message[4] = 'Active Links ' + str(data_abstract[u'Links actifs'])
                s.blanc_alternate = 3

            elif(s.blanc_alternate == 3):   # Online node
                s.message[4] = 'Online Links ' + str(data_abstract[u'Links connectés'])
                s.blanc_alternate = 4
                
            elif(s.blanc_alternate == 4):   # Total emission
                s.message[4] = 'Total Time ' + data_abstract[u'Emission cumulée']
                s.blanc_alternate = 5

            elif(s.blanc_alternate == 5):   # Last TX
                s.message[4] = 'Last TX ' + data_last[0][u'Heure']
                s.blanc_alternate = 0

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
