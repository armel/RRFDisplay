#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
RRFDisplay version Raspberry Pi 3B et Orange Pi Zero
Learn more about RRF on https://f5nlg.wordpress.com
Check video about RRFDisplay on https://www.youtube.com/watch?v=rVW8xczVpEo
73 & 88 de F4HWN Armel
'''

import settings as s
import display as d
import lib as l

import requests
import datetime
import time
import sys
import logging
import getopt
import configparser as cp
import RPi.GPIO as GPIO

from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas

from luma.oled.device import sh1106
from luma.oled.device import ssd1306
from luma.oled.device import ssd1327
from luma.oled.device import ssd1351
from luma.lcd.device  import st7735
from luma.core import cmdline, error

def main(argv):

    # Check and get arguments
    try:
        options, remainder = getopt.getopt(argv, '', ['help', 'interface=', 'spi-device=', 'i2c-port=', 'i2c-address=', 'framebuffer-device=', 'display=', 'display-width=', 'display-height=', 'display-theme=', 'follow=', 'refresh=', 'latitude=', 'longitude='])
    except getopt.GetoptError:
        l.usage()
        sys.exit(2)
    for opt, arg in options:
        if opt == '--help':
            l.usage()
            sys.exit()
        elif opt in ('--interface'):
            if arg not in ['i2c', 'spi', 'noop']:
                print('Unknown interface type (choose between \'i2c\', \'spi\' and \'noop\')')
                sys.exit()
            s.interface = arg
        elif opt in ('--framebuffer-device'):
            s.framebuffer_device = arg
        elif opt in ('--spi-device'):
            s.spi_device = int(arg)
        elif opt in ('--i2c-port'):
            s.i2c_port = int(arg)
        elif opt in ('--i2c-address'):
            s.i2c_address = int(arg, 16)
        elif opt in ('--display'):
            if arg not in ['sh1106', 'ssd1306', 'ssd1327', 'ssd1351', 'st7735', 'linux_framebuffer']:
                print('Unknown display type (choose between \'sh1106\', \'ssd1306\',  \'ssd1327\', \'ssd1351\', \'st7735\' and \'linux_framebuffer\')')
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
                follow = arg.split('/')
                for f in follow :
                    tmp = l.scan(f)
                    if tmp is False:
                        s.room_current = 'RRF'
                    else:
                        s.room_current = tmp
                        s.callsign = arg
                        s.scan = True
                        s.follow_list[f] = (tmp, f)
        elif opt in ('--refresh'):
            s.refresh = float(arg)
        elif opt in ('--latitude'):
            s.latitude = float(arg)
        elif opt in ('--longitude'):
            s.longitude = float(arg)
        elif opt in ('--display-theme'):
            indice = 0
            theme = arg.split('/')
            for f in s.follow_list:
                (follow, indicatif) = s.follow_list[f]
                print(f)
                s.theme_list[indicatif] = cp.ConfigParser()
                s.theme_list[indicatif].read('./themes/' + theme[i])
                indice += 1

    print(s.theme_list)
    # Set serial
    if s.interface == 'i2c':
        serial = i2c(port=s.i2c_port, address=s.i2c_address)
        if s.display == 'sh1106':
            s.device = sh1106(serial, width=s.display_width, height=s.display_height, rotate=0)
        elif s.display == 'ssd1306':
            s.device = ssd1306(serial, width=s.display_width, height=s.display_height, rotate=0)
        elif s.display == 'ssd1327':
            s.device = ssd1327(serial, width=s.display_width, height=s.display_height, rotate=0, mode='RGB')
    elif s.interface == 'spi':
        serial = spi(device=s.spi_device, port=0)
        if s.display == 'ssd1351':        
            s.device = ssd1351(serial, width=s.display_width, height=s.display_height, rotate=1, mode='RGB', bgr=True)
        elif s.display == 'st7735':
            s.device = st7735(serial, width=s.display_width, height=s.display_height, rotate=3, mode='RGB')
    else:
        config = ['--display=' + s.display, '--framebuffer-device=' + s.framebuffer_device, '--interface=' + s.interface]
        parser = cmdline.create_parser(description='RRFDisplay')
        args = parser.parse_args(config)
        s.device = cmdline.create_device(args)

    init_message = []

    # Let's go
    init_message.append('RRFDisplay ' + s.version)
    init_message.append('')
    init_message.append('88 et 73 de F4HWN')
    init_message.append('')
    d.display_init(init_message)

    # Lecture initiale de la progation et du cluster
    init_message.append('Requete Propagation')
    d.display_init(init_message)
    l.get_solar()

    init_message.append('Requete Cluster')
    d.display_init(init_message)
    l.get_cluster()

    init_message.append('Let\'s go')
    d.display_init(init_message)

    # Boucle principale
    s.timestamp_start = time.time()

    rrf_data = ''
    rrf_data_old = ''

    #print (follow_list)
    #print s.scan
    #print s.callsign
    #print s.room_current

    while(True):
        with canvas(s.device, dither=True) as draw:
            f_indice = 0
            for f in s.follow_list:
                f_indice += 1
                s.theme = s.theme_list[f]

                (s.room_current, s.callsign) = s.follow_list[f]

                chrono_start = time.time()

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
                        follow_list[f] = (tmp, s.callsign)
                        s.room_current = tmp

                if s.minute == 0: # Update solar propagation
                    l.get_solar()

                if s.minute % 4 == 0: # Update cluster
                    l.get_cluster()

                url = s.room[s.room_current]['url']

                # Requete HTTP vers le flux json du salon produit par le RRFDisplay 
                try:
                    r = requests.get(url, verify=False, timeout=0.5)
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

                if rrf_data != '' and rrf_data != rrf_data_old: # Si le flux est valide
                    rrf_data_old = rrf_data
                    data_abstract = rrf_data['abstract'][0]
                    data_activity = rrf_data['activity']
                    data_transmit = rrf_data['transmit'][0]
                    data_last = rrf_data['last']
                    data_all = rrf_data['all']

                    s.message[1] = l.sanitize_call(data_last[0]['Indicatif'])
                    s.message[2] = l.sanitize_call(data_last[1]['Indicatif'])
                    s.message[3] = l.sanitize_call(data_last[2]['Indicatif'])

                    if s.device.height >= 128:      # Only if place...
                        try:
                            data_elsewhere = rrf_data['elsewhere'][0]

                            i = 0
                            s.transmit_elsewhere = False
                            for data in rrf_data['elsewhere'][6]:
                                if data in ['RRF', 'TECHNIQUE', 'INTERNATIONAL', 'LOCAL', 'BAVARDAGE', 'FON']:
                                    tmp = rrf_data['elsewhere'][6][data]
                                    if tmp != 0:
                                        s.transmit_elsewhere = True
                                        s.raptor[i] = l.convert_second_to_time(tmp) + '/' + data[:3] + '/' + l.sanitize_call(rrf_data['elsewhere'][1][data]) + '/' + str(rrf_data['elsewhere'][5][data])
                                    else:
                                        s.raptor[i] = l.convert_second_to_time(tmp) + '/' + data[:3] + '/' + l.convert_time_to_string(rrf_data['elsewhere'][3][data]) + '/' + str(rrf_data['elsewhere'][5][data])

                                    i += 1
                        except:
                            pass

                    if data_transmit['Indicatif'] != '':
                        if s.transmit is False:      # Wake up screen...
                            s.transmit = l.wake_up_screen(s.device, s.display, s.transmit)

                        s.call_current = l.sanitize_call(data_transmit['Indicatif'])
                        s.call_type = data_transmit['Type']
                        s.call_description = data_transmit['Description']
                        s.call_tone = data_transmit['Tone']
                        s.call_locator = data_transmit['Locator']
                        s.call_sysop = data_transmit['Sysop']
                        s.call_prenom = data_transmit['Prenom']
                        s.call_latitude = data_transmit['Latitude']
                        s.call_longitude = data_transmit['Longitude']

                        s.duration = data_transmit['TOT']

                    else:
                        if s.transmit is True:       # Sleep screen...
                            s.transmit = l.wake_up_screen(s.device, s.display, s.transmit)

                        # Load Histogram
                        for q in range(0, 24):
                            s.qso_hour[q] = data_activity[q]['TX']

                        # Load Last
                        limit = len(rrf_data['last'])
                        s.call = [''] * 10 
                        s.call_time = [''] * 10 

                        for q in range(0, limit):
                            s.call[q] = l.sanitize_call(rrf_data['last'][q]['Indicatif'])
                            s.call_time[q] = rrf_data['last'][q]['Heure']

                        # Load Best
                        limit = len(rrf_data['all'])
                        s.best = [''] * 10 
                        s.best_time = [0] * 10 

                        for q in range(0, limit):
                            s.best[q] = l.sanitize_call(rrf_data['all'][q]['Indicatif'])
                            s.best_time[q] = l.convert_time_to_second(rrf_data['all'][q]['Durée'])

                    if(s.seconde < 10):     # TX today
                        s.message[0] = 'TX total ' + str(data_abstract['TX total'])

                    elif(s.seconde < 20):   # Active node
                        s.message[0] = 'Links actifs ' + str(data_abstract['Links actifs'])

                    elif(s.seconde < 30):   # Online node
                        s.message[0] = 'Links total ' + str(data_abstract['Links connectés'])
                        
                    elif(s.seconde < 40):   # Total emission
                        tmp = l.convert_time_to_string(data_abstract['Emission cumulée'])
                        if 'h' in tmp:
                            tmp = tmp[0:6]
                        s.message[0] = 'BF total ' + tmp

                    elif(s.seconde < 50):   # Last TX
                        s.message[0] = 'Dernier ' + data_last[0]['Heure']

                    elif(s.seconde < 60):   # Scan
                        if s.scan is True:
                            s.message[0] = 'Suivi de ' + s.callsign
                        else:
                            s.message[0] = 'Salon ' + s.room_current[:3]

                # Print screen
                if f_indice == 1:
                    d.display_gateway(draw, 20)
                else:
                    d.display_gateway(draw, 170)
                   
            chrono_stop = time.time()
            chrono_time = chrono_stop - chrono_start
            if chrono_time < s.refresh:
                sleep = s.refresh - chrono_time
            else:
                sleep = 0
            #print "Temps d'execution : %.2f %.2f secondes" % (chrono_time, sleep)
            #sys.stdout.flush()

            time.sleep(sleep)
            #GPIO.cleanup()

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
