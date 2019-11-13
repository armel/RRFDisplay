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
        options, remainder = getopt.getopt(argv, '', ['help', 'i2c-port=', 'i2c-address=', 'display=', 'display-width=', 'display-height=', 'room=', 'callsign=', 'latitude=', 'longitude='])
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
        elif opt in ('--callsign'):
            s.callsign = arg
        elif opt in ('--room'):
            if arg not in ['RRF', 'TECHNIQUE', 'INTERNATIONAL', 'LOCAL', 'BAVARDAGE', 'FON', 'SCAN']:
                print 'Unknown room name (choose between \'RRF\', \'TECHNIQUE\', \'INTERNATIONAL\', \'LOCAL\', \'BAVARDAGE\', \'FON\' or \'SCAN\')'
                sys.exit()
            if arg == 'SCAN':
                s.scan = True
                s.room_current = 'RRF'
                l.scan()
            else:
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

    # Boucle principale
    s.timestamp_start = time.time()

    rrf_data = ''

    while(True):
        tmp = datetime.datetime.now()
        s.day = tmp.strftime('%Y-%m-%d')
        s.now = tmp.strftime('%H:%M:%S')
        s.hour = int(tmp.strftime('%H'))
        s.minute = int(s.now[3:-3])
        s.seconde = int(s.now[-2:])

        if s.seconde % 15 == 0 and s.scan == True: # On scan
            l.scan()

        url = s.room[s.room_current]['url']

        # Requete HTTP vers le flux json du salon produit par le RRFTracker 
        try:
            r = requests.get(url, verify=False, timeout=1)
        except requests.exceptions.ConnectionError as errc:
            print ('Error Connecting:', errc)
        except requests.exceptions.Timeout as errt:
            print ('Timeout Error:', errt)

        # Controle de la validité du flux json
        try:
            rrf_data = r.json()
        except:
            pass

        if rrf_data != '': # Si le flux est valide
            data_abstract = rrf_data['abstract'][0]
            data_activity = rrf_data['activity']
            data_transmit = rrf_data['transmit'][0]
            data_last = rrf_data['last']
            data_all = rrf_data['all']

            s.message[0] = l.sanitize_call(data_last[2][u'Indicatif'].encode('utf-8'))
            s.message[1] = l.sanitize_call(data_last[1][u'Indicatif'].encode('utf-8'))
            s.message[2] = l.sanitize_call(data_last[0][u'Indicatif'].encode('utf-8'))

            if s.device.height == 128:      # Only if place...
                try:
                    data_elsewhere = rrf_data['elsewhere'][0]

                    i = 0
                    s.transmit_elsewhere = False
                    for data in rrf_data['elsewhere'][6]:
                        if data in ['RRF', 'TECHNIQUE', 'INTERNATIONAL', 'LOCAL', 'BAVARDAGE', 'FON']:
                            tmp = rrf_data['elsewhere'][6][data]
                            if tmp != 0:
                                s.transmit_elsewhere = True
                                s.raptor[i] = str(1) + '/' + data[:3] + '/' + l.sanitize_call(rrf_data['elsewhere'][1][data].encode('utf-8')) + '/' + str(rrf_data['elsewhere'][5][data])
                            else:
                                s.raptor[i] = str(0) + '/' + data[:3] + '/' + rrf_data['elsewhere'][3][data] + '/' + str(rrf_data['elsewhere'][5][data])

                            i += 1
                except:
                    pass

            if data_transmit['Indicatif'] != '':
                if s.transmit is False:      # Wake up screen...
                    s.transmit = l.wake_up_screen(s.device, s.display, s.transmit)

                s.call_current = l.sanitize_call(data_transmit[u'Indicatif'].encode('utf-8'))
                s.duration = data_transmit[u'TOT']

            else:
                if s.transmit is True:       # Sleep screen...
                    s.transmit = l.wake_up_screen(s.device, s.display, s.transmit)

                # Load Histogram
                for q in xrange(0, 24):
                    s.qso_hour[q] = data_activity[q][u'TX']

                # Load Last
                limit = len(rrf_data['last'])
                s.call = [''] * 10 
                s.call_time = [''] * 10 

                for q in xrange(0, limit):
                    s.call[q] = l.sanitize_call(rrf_data['last'][q][u'Indicatif'].encode('utf-8'))
                    s.call_time[q] = rrf_data['last'][q][u'Heure']

                # Load Best
                limit = len(rrf_data['all'])
                s.best = [''] * 10 
                s.best_time = [0] * 10 

                for q in xrange(0, limit):
                    s.best[q] = l.sanitize_call(rrf_data['all'][q][u'Indicatif'].encode('utf-8'))
                    s.best_time[q] = l.convert_time_to_second(rrf_data['all'][q][u'Durée'])

            if(s.seconde < 10):     # TX today
                s.message[4] = 'TX total ' + str(data_abstract[u'TX total'])

            elif(s.seconde < 20):   # Active node
                s.message[4] = 'Links actifs ' + str(data_abstract[u'Links actifs'])

            elif(s.seconde < 30):   # Online node
                s.message[4] = 'Links connectés ' + str(data_abstract[u'Links connectés'])
                
            elif(s.seconde < 40):   # Total emission
                s.message[4] = 'BF total ' + data_abstract[u'Emission cumulée']

            elif(s.seconde < 50):   # Last TX
                s.message[4] = 'Dernier TX ' + data_last[0][u'Heure']
                s.blanc_alternate = 6

            elif(s.seconde < 60):   # Scan
                if s.scan is True:
                    s.message[4] = 'Suivi de ' + s.callsign
                else:
                    s.message[4] = 'Salon ' + s.room_current[:3]         

        # Print screen
        if s.device.height == 128:
            d.display_128()
        elif s.device.height == 64:
            d.display_64()
        else:
            d.display_32()

        time.sleep(0.5)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
