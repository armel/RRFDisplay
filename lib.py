#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
RRFDisplay version Raspberry Pi 3B et Orange Pi Zero
Learn more about RRF on https://f5nlg.wordpress.com
Check video about RRFDisplay on https://www.youtube.com/watch?v=rVW8xczVpEo
73 & 88 de F4HWN Armel
'''

import os
import requests
import sys
import getopt
import json
import urllib3
import calendar

urllib3.disable_warnings()

import settings as s

from math import cos, asin, sqrt, ceil
from lxml import etree
from datetime import datetime, timedelta

# Usage
def usage():
    print('Usage: RRFDisplay.py [options ...]')
    print()
    print('--help               this help')
    print()
    print('Interface settings :')
    print('  --interface        set interface (default=i2c, choose between [i2c, spi])')
    print('  --i2c-port         set i2c port (default=0)')
    print('  --i2c-address      set i2c address (default=0x3C)')
    print()
    print('Display settings :')
    print('  --display          set display (default=sh1106, choose between [sh1106, ssd1306, ssd1327, ssd1351, st7735])')
    print('  --display-width    set display width (default=128)')
    print('  --display-height   set display height (default=64)')
    print('  --display-theme    set display theme (default=theme.cfg)')
    print()
    print('Follow settings :')
    print('  --follow           set room (default=RRF, choose between [RRF, TECHNIQUE, INTERNATIONAL, LOCAL, BAVARDAGE, FON]) or callsign to follow')
    print('  --refresh          set refresh (default=1, in second)')
    print()
    print('WGS84 settings :')
    print('  --latitude         set latitude (default=48.8483808, format WGS84)')
    print('  --longitude        set longitude (default=2.2704347, format WGS84)')
    print()
    print('88 & 73 from F4HWN Armel')


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
def wake_up_screen(device, display, wake_up):
    if 'sh1106' in display:
        level_sleep = 4
        level_wake_up = 150
    elif 'ssd1306' in display:
        level_sleep = 4
        level_wake_up = 150
    elif 'ssd1327' in display:
        level_sleep = 4
        level_wake_up = 15
    elif 'ssd1351' in display:
        level_sleep = 50
        level_wake_up = 150
    else:
        level_sleep = 4
        level_wake_up = 150

    if wake_up is True:
        for i in range(level_wake_up, level_sleep, -1):
            device.contrast(i)         # No Transmitter
        return False
    else:
        for i in range(level_sleep, level_wake_up):
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
        #mem_total = int(tmp[1][:-1])
        #mem_use = int(tmp[2][:-1])

        mem_total = int(tmp[1][:-2])
        mem_use = int(tmp[2][:-2])

        return str(int((float(mem_use) / float(mem_total)) * 100)), str(mem)

    elif value == 'disk':
        tmp = list(os.popen('df -h /dev/mmcblk0p1'))
        tmp = tmp[1].strip()
        tmp = tmp.split()

        disk_total = tmp[1]
        disk_use = tmp[4]
        
        return str(disk_use), str(disk_total)

    elif value == 'load':
        tmp = list(os.popen('w | head -n 1'))
        tmp = tmp[0].strip()
        tmp = tmp.split()

        return str(tmp[-3]) + ' ' + str(tmp[-2]) + ' ' + str(tmp[-1])

    elif value == 'up':
        tmp = list(os.popen('uptime -p'))
        tmp = tmp[0].strip()
        tmp = [int(s) for s in tmp.split() if s.isdigit()]

        if len(tmp) == 3:
            day = tmp[0]
            hour = tmp[1]
            minute = tmp[2]
        elif len(tmp) == 2:
            day = 0
            hour = tmp[0]
            minute = tmp[1]
        else:
            day = 0
            hour = 0
            minute = tmp[0]

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

        return str(tmp)

    elif value == 'ip':
        tmp = list(os.popen('hostname -I'))
        tmp = tmp[0].strip()
        tmp = tmp.split()
        tmp = tmp[0]

        return str(tmp)

    elif value == 'arch':
        tmp = os.popen('uname -a').readline()
        if 'sunxi' in tmp:
            tmp = 'Orange Pi'
        else:
            tmp = 'Raspberry Pi'
        return str(tmp)

    elif value == 'kernel':
        tmp = os.popen('uname -r').readline()
        return str(tmp)

# Compute distance
def calc_distance(call, latitude_1, longitude_1):
    latitude_2 = float(s.call_latitude)
    longitude_2 = float(s.call_longitude)
    
    if (latitude_2 + longitude_2) != 0:
        p = 0.017453292519943295        # Approximation Pi/180
        a = 0.5 - cos((latitude_2 - latitude_1) * p) / 2 + cos(latitude_1 * p) * cos(latitude_2 * p) * (1 - cos((longitude_2 - longitude_1) * p)) / 2
        r = (12742 * asin(sqrt(a)))
        if r < 100:
            r = round((12742 * asin(sqrt(a))), 1)
        else:
            r = int(ceil(12742 * asin(sqrt(a))))
        return r
    return False

# Convert second to time
def convert_second_to_time(time):
    hours = time // 3600
    time = time - (hours * 3600)

    minutes = time // 60
    seconds = time - (minutes * 60)

    if hours == 0:
        return str('{:0>2d}'.format(int(minutes))) + ':' + str('{:0>2d}'.format(int(seconds)))
    else:
        return str('{:0>2d}'.format(int(hours))) + ':' + str('{:0>2d}'.format(int(minutes))) + ':' + str('{:0>2d}'.format(int(seconds)))

# Convert time to second
def convert_time_to_second(time):
    if len(time) > 5:
        format = [3600, 60, 1]
    else:
        format = [60, 1]        
    
    return sum([a * b for a, b in zip(format, list(map(int, time.split(':'))))])

# Convert time to second
def convert_time_to_string(time):
    if len(time) == 5:
        time = '00:' + time

    time = time.replace(':', 'h ', 1)
    time = time.replace(':', 'm ', 1) + 's'

    return time

# Convert time utc to time local
def utc_to_local(utc_dt):
    utc_dt = datetime.strptime(utc_dt, '%Y-%m-%d %H:%M:%S')
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    assert utc_dt.resolution >= timedelta(microseconds=1)
    return local_dt.replace(microsecond=utc_dt.microsecond)

# Sanitize call
def sanitize_call(call):
    return call.translate(str.maketrans('', '', '\\\'!@#$"()[]'))

# Scan
def scan(call):
    try:
        r = requests.get(s.room[s.room_current]['api'], verify=False, timeout=10)
        page = r.content
        print(type(page))
        print(type(call))
        print(type(str(page)))
        if call in page:
            return s.room_current
    except requests.exceptions.ConnectionError as errc:
        return False
    except requests.exceptions.Timeout as errt:
        return False

    else:
        for q in ['RRF', 'TECHNIQUE', 'INTERNATIONAL', 'LOCAL', 'BAVARDAGE', 'FON']:
            if q != s.room:
                try:
                    r = requests.get(s.room[q]['api'], verify=False, timeout=10)
                    page = r.content
                    if call in page:
                        return q
                except requests.exceptions.ConnectionError as errc:
                    return False
                except requests.exceptions.Timeout as errt:
                    return False
    
    return False

# Get solar propagation

def get_solar():
    solar_data = ''

    # Get date
    now = datetime.now() - timedelta(minutes=60)
    today = format(now, "%Y-%m-%d %H:%M:%S")

    # Check file
    if os.path.isfile(s.solar_file):
        modify = datetime.fromtimestamp(os.path.getmtime(s.solar_file)).strftime("%Y-%m-%d %H:%M:%S")

    if not os.path.isfile(s.solar_file) or today > modify or len(s.solar_value) == 0:     # if necessary update file
        # Request HTTP on hamqsl
        try:
            r = requests.get(s.solar_url, verify=False, timeout=1)
            solar_data = etree.fromstring(r.content)
            f = open(s.solar_file, 'w')
            f.write(r.content)
            f.close
        except:
            pass

        if solar_data != '': # If valid stream
            s.solar_value.clear()
            # Page 1
            for value in solar_data.xpath('/solar/solardata/updated'):
                s.solar_value['Updated'] = value.text.strip()
                
                tmp = s.solar_value['Updated'].split(' ')
                tmp = tmp[0] + ' ' + tmp[1] + ' ' + tmp[2] + ' ' + tmp[3]
                tmp = datetime.strptime(tmp, '%d %b %Y %H%M')

                s.solar_value['Updated'] = tmp.strftime("%d-%m, %H:%M")

            for value in solar_data.xpath('/solar/solardata/solarflux'):
                s.solar_value['Solar Flux'] = value.text.strip()
            for value in solar_data.xpath('/solar/solardata/aindex'):
                s.solar_value['A-Index'] = value.text.strip()
            for value in solar_data.xpath('/solar/solardata/kindex'):
                s.solar_value['K-Index'] = value.text.strip()
            for value in solar_data.xpath('/solar/solardata/sunspots'):
                s.solar_value['Sun Spots'] = value.text.strip()
            for value in solar_data.xpath('/solar/solardata/xray'):
                s.solar_value['X-Ray'] = value.text.strip()
            for value in solar_data.xpath('/solar/solardata/protonflux'):
                s.solar_value['Ptn Flux'] = value.text.strip()
            for value in solar_data.xpath('/solar/solardata/electonflux'):
                s.solar_value['Elc Flux'] = value.text.strip()
            for value in solar_data.xpath('/solar/solardata/magneticfield'):
                s.solar_value['Mag (BZ)'] = value.text.strip()
            for value in solar_data.xpath('/solar/solardata/solarwind'):
                s.solar_value['Solar Wind'] = value.text.strip()

            # Page 2
            for value in solar_data.xpath('/solar/solardata/calculatedconditions/band[@name="80m-40m" and @time="day"]'):
                s.solar_value['80m-40m Day'] = value.text.strip()
            for value in solar_data.xpath('/solar/solardata/calculatedconditions/band[@name="30m-20m" and @time="day"]'):
                s.solar_value['30m-20m Day'] = value.text.strip()
            for value in solar_data.xpath('/solar/solardata/calculatedconditions/band[@name="17m-15m" and @time="day"]'):
                s.solar_value['17m-15m Day'] = value.text.strip()
            for value in solar_data.xpath('/solar/solardata/calculatedconditions/band[@name="12m-10m" and @time="day"]'):
                s.solar_value['12m-10m Day'] = value.text.strip()

            for value in solar_data.xpath('/solar/solardata/calculatedconditions/band[@name="80m-40m" and @time="night"]'):
                s.solar_value['80m-40m Night'] = value.text.strip()
            for value in solar_data.xpath('/solar/solardata/calculatedconditions/band[@name="30m-20m" and @time="night"]'):
                s.solar_value['30m-20m Night'] = value.text.strip()
            for value in solar_data.xpath('/solar/solardata/calculatedconditions/band[@name="17m-15m" and @time="night"]'):
                s.solar_value['17m-15m Night'] = value.text.strip()
            for value in solar_data.xpath('/solar/solardata/calculatedconditions/band[@name="12m-10m" and @time="night"]'):
                s.solar_value['12m-10m Night'] = value.text.strip()

            for value in solar_data.xpath('/solar/solardata/geomagfield'):
                s.solar_value['Geomag Field'] = value.text.strip()
                s.solar_value['Geomag Field'] = s.solar_value['Geomag Field'].title()
            for value in solar_data.xpath('/solar/solardata/signalnoise'):
                s.solar_value['Signal Noise'] = value.text.strip()

            # Page 3
            for value in solar_data.xpath('/solar/solardata/calculatedvhfconditions/phenomenon[@name="vhf-aurora" and @location="northern_hemi"]'):
                s.solar_value['VHF Aurora'] = value.text.strip()
                s.solar_value['VHF Aurora'] = s.solar_value['VHF Aurora'].replace('Band ', '')
            for value in solar_data.xpath('/solar/solardata/calculatedvhfconditions/phenomenon[@name="E-Skip" and @location="europe"]'):
                s.solar_value['E-Skip EU 2m'] = value.text.strip()
                s.solar_value['E-Skip EU 2m'] = s.solar_value['E-Skip EU 2m'].replace('Band ', '')
            for value in solar_data.xpath('/solar/solardata/calculatedvhfconditions/phenomenon[@name="E-Skip" and @location="europe_4m"]'):
                s.solar_value['E-Skip EU 4m'] = value.text.strip()
                s.solar_value['E-Skip EU 4m'] = s.solar_value['E-Skip EU 4m'].replace('Band ', '')
            for value in solar_data.xpath('/solar/solardata/calculatedvhfconditions/phenomenon[@name="E-Skip" and @location="europe_6m"]'):
                s.solar_value['E-Skip EU 6m'] = value.text.strip()
                s.solar_value['E-Skip EU 6m'] = s.solar_value['E-Skip EU 6m'].replace('Band ', '')
            for value in solar_data.xpath('/solar/solardata/calculatedvhfconditions/phenomenon[@name="E-Skip" and @location="north_america"]'):
                s.solar_value['E-Skip NA 2m'] = value.text.strip()
                s.solar_value['E-Skip NA 2m'] = s.solar_value['E-Skip NA 2m'].replace('Band ', '')

    return True

# Get cluster

def get_cluster():
    cluster_data = ''

    # Get date
    now = datetime.now() - timedelta(minutes=4)
    today = format(now, "%Y-%m-%d %H:%M:%S")

    # Check file
    if os.path.isfile(s.cluster_file):
        modify = datetime.fromtimestamp(os.path.getmtime(s.cluster_file)).strftime("%Y-%m-%d %H:%M:%S")

    if not os.path.isfile(s.cluster_file) or today > modify or len(s.cluster_value) == 0:     # if necessary update file
        if os.path.isfile(s.cluster_band_file):
            with open(s.cluster_band_file, 'r') as f:
                band = f.read().strip()
        else:
            band = s.cluster_band

        # Request HTTP on hamqsl
        try:
            r = requests.get(s.cluster_url + band, verify=False, timeout=1)
            cluster_data = r.json()
            f = open(s.cluster_file, 'w')
            f.write(r.content)
            f.close
        except:
            pass

        if cluster_data != '':
            s.cluster_value.clear()
            limit = len(cluster_data)
            indice = 0
            for item in range(0, limit):
                if band in s.cluster_exclude:
                    if str(int(float(cluster_data[item]['freq']))) not in s.cluster_exclude[band]:
                        s.cluster_value[indice] = cluster_data[item]['call'] + ' ' + cluster_data[item]['freq'] + ' ' + cluster_data[item]['dxcall'] + ' ' + str(utc_to_local(cluster_data[item]['time']))
                else:
                    s.cluster_value[indice] = cluster_data[item]['call'] + ' ' + cluster_data[item]['freq'] + ' ' + cluster_data[item]['dxcall'] + ' ' + str(utc_to_local(luster_data[item]['time']))

                indice += 1
                if indice == 10:
                    break

    return True  