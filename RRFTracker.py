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
import configparser as cp

from luma.core.interface.serial import i2c, spi
from luma.oled.device import sh1106
from luma.oled.device import ssd1306
from luma.oled.device import ssd1327
from luma.oled.device import ssd1351
from luma.lcd.device  import st7735

from luma.core.render import canvas

def main(argv):

    # Check and get arguments
    try:
        options, remainder = getopt.getopt(argv, '', ['help', 'interface=', 'i2c-port=', 'i2c-address=', 'display=', 'display-width=', 'display-height=', 'display-theme=', 'follow=', 'latitude=', 'longitude='])
    except getopt.GetoptError:
        l.usage()
        sys.exit(2)
    for opt, arg in options:
        if opt == '--help':
            l.usage()
            sys.exit()
        elif opt in ('--interface'):
            if arg not in ['i2c', 'spi']:
                print 'Unknown interface type (choose between \'i2c\' and \'spi\')'
                sys.exit()
            s.interface = arg
        elif opt in ('--i2c-port'):
            s.i2c_port = int(arg)
        elif opt in ('--i2c-address'):
            s.i2c_address = int(arg, 16)
        elif opt in ('--display'):
            if arg not in ['sh1106', 'ssd1306', 'ssd1327', 'ssd1351', 'st7735']:
                print 'Unknown display type (choose between \'sh1106\', \'ssd1306\',  \'ssd1327\', \'ssd1351\' and \'st7735\')'
                sys.exit()
            s.display = arg
        elif opt in ('--display-width'):
            s.display_width = int(arg)
        elif opt in ('--display-height'):
            s.display_height = int(arg)
        elif opt in ('--follow'):
            if arg in ['RRF', 'TECHNIQUE', 'INTERNATIONAL', 'LOCAL', 'BAVARDAGE', 'FON']:
                s.room_current = arg
            else:
                s.room_current = 'RRF'
                tmp = l.scan(arg)
                if tmp is False:
                    s.room_current = 'RRF'
                else:
                    s.room_current = tmp
                    s.callsign = arg
                    s.scan = True

        elif opt in ('--latitude'):
            s.latitude = float(arg)
        elif opt in ('--longitude'):
            s.longitude = float(arg)
        elif opt in ('--display-theme'):
            s.display_theme = arg

    # Set serial
    if s.interface == 'i2c':
        serial = i2c(port=s.i2c_port, address=s.i2c_address)
        if s.display == 'sh1106':
            s.device = sh1106(serial, width=s.display_width, height=s.display_height, rotate=0)
        elif s.display == 'ssd1306':
            s.device = ssd1306(serial, width=s.display_width, height=s.display_height, rotate=0)
        elif s.display == 'ssd1327':
            s.device = ssd1327(serial, width=s.display_width, height=s.display_height, rotate=0, mode='RGB')
    else:
        serial = spi(device=0, port=0)
        if s.display == 'ssd1351':        
            s.device = ssd1351(serial, width=s.display_width, height=s.display_height, rotate=1, mode='RGB', bgr=True)
        elif s.display == 'st7735':
            s.device = st7735(serial, width=s.display_width, height=s.display_height, mode='RGB')


    # Lecture du fichier de theme
    s.theme = cp.ConfigParser()
    s.theme.read('./themes/' + s.display_theme)

    print s.display_theme

    # Boucle principale
    s.timestamp_start = time.time()

    rrf_data = ''

    #print s.scan
    #print s.callsign
    #print s.room_current

    while(True):
        tmp = datetime.datetime.now()
        s.day = tmp.strftime('%Y-%m-%d')
        s.now = tmp.strftime('%H:%M:%S')
        s.hour = int(tmp.strftime('%H'))
        s.minute = int(s.now[3:-3])
        s.seconde = int(s.now[-2:])

        if s.seconde % 15 == 0 and s.scan == True: # On scan
            tmp = l.scan(s.callsign)
            if tmp is not False:
                #print s.now, tmp
                s.room_current = tmp

        url = s.room[s.room_current]['url']

        # Requete HTTP vers le flux json du salon produit par le RRFTracker 
        try:
            r = requests.get(url, verify=False, timeout=0.30)
        except requests.exceptions.ConnectionError as errc:
            #print ('Error Connecting:', errc)
            pass
        except requests.exceptions.Timeout as errt:
            #print ('Timeout Error:', errt)
            pass

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

            s.message[1] = l.sanitize_call(data_last[0][u'Indicatif'].encode('utf-8'))
            s.message[2] = l.sanitize_call(data_last[1][u'Indicatif'].encode('utf-8'))
            s.message[3] = l.sanitize_call(data_last[2][u'Indicatif'].encode('utf-8'))

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
                                s.raptor[i] = l.convert_second_to_time(tmp) + '/' + data[:3] + '/' + l.sanitize_call(rrf_data['elsewhere'][1][data].encode('utf-8')) + '/' + str(rrf_data['elsewhere'][5][data])
                            else:
                                s.raptor[i] = l.convert_second_to_time(tmp) + '/' + data[:3] + '/' + rrf_data['elsewhere'][3][data] + '/' + str(rrf_data['elsewhere'][5][data])

                            i += 1
                except:
                    pass

            if data_transmit['Indicatif'] != '':
                if s.transmit is False:      # Wake up screen...
                    s.transmit = l.wake_up_screen(s.device, s.display, s.transmit)

                s.call_current = l.sanitize_call(data_transmit[u'Indicatif'].encode('utf-8'))
                s.call_type = data_transmit[u'Type'].encode('utf-8')
                s.call_description = data_transmit[u'Description'].encode('utf-8')
                s.call_tone = data_transmit[u'Tone'].encode('utf-8')
                s.call_locator = data_transmit[u'Locator'].encode('utf-8')
                s.call_sysop = data_transmit[u'Sysop'].encode('utf-8')
                s.call_latitude = data_transmit[u'Latitude']
                s.call_longitude = data_transmit[u'Longitude']

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
                s.message[0] = 'TX total ' + str(data_abstract[u'TX total'])

            elif(s.seconde < 20):   # Active node
                s.message[0] = 'Links actifs ' + str(data_abstract[u'Links actifs'])

            elif(s.seconde < 30):   # Online node
                s.message[0] = 'Links total ' + str(data_abstract[u'Links connectés'])
                
            elif(s.seconde < 40):   # Total emission
                s.message[0] = 'BF total ' + data_abstract[u'Emission cumulée']

            elif(s.seconde < 50):   # Last TX
                s.message[0] = 'Dernier ' + data_last[0][u'Heure']

            elif(s.seconde < 60):   # Scan
                if s.scan is True:
                    s.message[0] = 'Suivi de ' + s.callsign
                else:
                    s.message[0] = 'Salon ' + s.room_current[:3]         

        # Print screen
        if s.device.height == 128:
            d.display_128()
        else:
            d.display_64()

        time.sleep(0.25)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
