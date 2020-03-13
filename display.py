#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
RRFTracker version Raspberry Pi 3B et Orange Pi Zero
Learn more about RRF on https://f5nlg.wordpress.com
Check video about RRFTracker on https://www.youtube.com/watch?v=rVW8xczVpEo
73 & 88 de F4HWN Armel
'''

import settings as s
import lib as l
import time

from luma.core.render import canvas
from luma.core import legacy

from PIL import ImageFont

icon = ImageFont.truetype('fonts/fontello.ttf', 14)     # Icon font
font = ImageFont.truetype('fonts/7x5.ttf', 8)           # Text font
font_tot = ImageFont.truetype('fonts/astro.ttf', 52)    # Text font

# Manage color
def get_color(section, value):
    color = s.theme.get(section, value)
    if color in s.color:
        return s.color[color]
    else:
        return color

# Draw label
def label(draw, position, width, bg_color, fg_color, label, value, fixed = 0):
    if s.device.height == 128:
        position += 3
        draw.rectangle((0, position - 1, width, position + 8), fill=bg_color)
        draw.line((width + 1, position, width + 1, position + 7), fill=bg_color)
        draw.line((width + 2, position + 1, width + 2, position + 6), fill=bg_color)
        draw.line((width + 3, position + 2, width + 3, position + 5), fill=bg_color)
        draw.line((width + 4, position + 3, width + 4, position + 4), fill=bg_color)
    else:
        draw.rectangle((0, position - 1, width, position + 7), fill=bg_color)
        draw.line((width + 1, position, width + 1, position + 6), fill=bg_color)
        draw.line((width + 2, position + 1, width + 2, position + 5), fill=bg_color)
        draw.line((width + 3, position + 2, width + 3, position + 4), fill=bg_color)

    draw.text((1, position), label, font=font, fill=fg_color)
    if fixed == 0:
        draw.text((width + 10, position), value, font=font, fill=get_color('screen', 'foreground'))
    else:
        draw.text((fixed, position), value, font=font, fill=get_color('screen', 'foreground'))        

# Draw tot
def tot(draw, legacy, duration, position):
    #duration += (duration / 60)     # Reajust time latence
    if s.device.height < 128:
        j = 54
        k = 11

        duration_min = 0

        timer = [i for i in xrange(60, 360, 60)]

        for i in timer:
            if duration < i:
                duration_max = i
                break
            else:
                duration_min = i

        h = l.interpolation(duration, duration_min, duration_max, 0, 120)

        draw.rectangle((0, j, 128, j - k), fill=get_color('screen', 'background'))
        for i in xrange(3, h, 2):
            draw.rectangle((i, j, i, j - k), fill=get_color('screen', 'foreground'))

        for i in xrange(0, 128, 4):
            draw.line((i, position, i + 1, position), fill=get_color('screen', 'foreground'))

        # Duration min
        tmp = list(str(duration_min))
        msg = ''
        for c in tmp:
            msg += chr(s.letter[c])
        legacy.text(draw, (0, position + 2), msg, fill=get_color('screen', 'foreground'), font=s.SMALL_BITMAP_FONT)

        # Duration max
        tmp = list(str(duration_max))
        msg = ''
        for c in tmp:
            msg += chr(s.letter[c])
        if duration_max < 100:
            tab = 4
        else:
            tab = 0
        legacy.text(draw, (115 + tab, position + 2), msg, fill=get_color('screen', 'foreground'), font=s.SMALL_BITMAP_FONT)

        # duration
        tmp = list(str(duration))
        msg = ''
        for c in tmp:
            msg += chr(s.letter[c])
        if duration < 10:
            tab = 2
        else:
            tab = 0

        legacy.text(draw, (60 + tab, position + 2), msg, fill=get_color('screen', 'foreground'), font=s.SMALL_BITMAP_FONT)
    else:
        draw.text((8, 28), l.convert_second_to_time(duration), font=font_tot, fill=get_color('tot', 'foreground'))


# Print elsewhere
def elsewhere(draw, data):
    draw.rectangle((0, 77, 127, 127), outline=get_color('elsewhere', 'border'), fill=get_color('elsewhere', 'background'))

    # Horizontal

    for i in [87, 97, 107, 117]:
        draw.line((0,  i, 127,  i), fill=get_color('elsewhere', 'border'))

    i = 79
    for d in data:
        d = d.split('/')
        tmp = d[2].split(':')
        if len(tmp) == 2:
            tmp = '00:' + tmp[0] + ':' + tmp[1]
            d[2] = tmp

        if d[0] == '00:00':
            draw.rectangle((21, i - 1, 126, i + 7), fill=get_color('elsewhere', 'background'))
            draw.text((24, i), d[2], font=font, fill=get_color('elsewhere', 'foreground'))
            draw.text((98, i), d[3], font=font, fill=get_color('elsewhere', 'foreground'))
        else:
            draw.rectangle((21, i - 1, 126, i + 7), fill=get_color('elsewhere', 'background_active'))
            draw.text((24, i), d[2], font=font, fill=get_color('elsewhere', 'foreground_active'))
            draw.text((98, i), d[3], font=font, fill=get_color('elsewhere', 'foreground_active'))

        draw.rectangle((1, i - 1, 19, i + 7), fill=get_color('elsewhere', 'background_active'))
        draw.text(( 2, i), d[1], font=font, fill=get_color('elsewhere', 'foreground_active'))

        i += 10

    # Vertical

    draw.line((20, 77, 20, 127), fill=get_color('elsewhere', 'border'))
    draw.line((94, 77, 94, 127), fill=get_color('elsewhere', 'border'))


# Print whois
def whois(draw):
    draw.rectangle((0, 77, 127, 127), outline=get_color('whois', 'border'), fill=get_color('whois', 'background'))
    draw.rectangle((1, 78,  47, 126), fill=get_color('whois', 'background_active'))

    # Vertical

    draw.line((48, 77,  48, 127), fill=get_color('whois', 'border'))

    # Horizontal

    for i in [87, 97, 107, 117]:
        draw.line((0,  i, 127,  i), fill=get_color('whois', 'border'))

    draw.text((2, 79), 'Type', font=font, fill=get_color('whois', 'foreground_active'))
    draw.text((50, 79), s.call_type, font=font, fill=get_color('whois', 'foreground'))

    draw.text((2, 89), 'Detail', font=font, fill=get_color('whois', 'foreground_active'))
    if len(s.call_description) > 14:
        draw.text((50, 89), s.call_description[:14] + '...', font=font, fill=get_color('whois', 'foreground'))
    else:
        draw.text((50, 89), s.call_description, font=font, fill=get_color('whois', 'foreground'))

    draw.text((2, 99), 'Tone', font=font, fill=get_color('whois', 'foreground_active'))
    draw.text((50, 99), s.call_tone, font=font, fill=get_color('whois', 'foreground'))

    draw.text((2, 109), 'Locator', font=font, fill=get_color('whois', 'foreground_active'))
    draw.text((50, 109), s.call_locator, font=font, fill=get_color('whois', 'foreground'))

    draw.text((2, 119), 'Sysop', font=font, fill=get_color('whois', 'foreground_active'))
    draw.text((50, 119), s.call_sysop, font=font, fill=get_color('whois', 'foreground'))

# Draw histogram
def histogram(draw, legacy, position, height = 15):
    qso_hour_max = max(s.qso_hour)

    i = 5
    j = 100

    for (t, q) in enumerate(s.qso_hour):
        if q != 0:
            h = l.interpolation(q, 0, qso_hour_max, 0, height)
        else:
            h = 0

        draw.rectangle((0 + i, position, i + 2, (position - height)), fill=get_color('screen', 'background'))
        if t == s.hour:
            color = get_color('histogram', 'column_current')
        else:
            color = get_color('histogram', 'column')

        draw.rectangle((0 + i, position, i + 2, (position - h)), fill=color)
        
        j += 5
        i += 5

    for i, j, k in [(1, 0, 0), (33, 0, 6), (63, 1, 2), (93, 1, 8), (120, 2, 3)]:
        legacy.text(draw, (i, position + 2), chr(j) + chr(k), fill=get_color('histogram', 'legend'), font=s.SMALL_BITMAP_FONT)

# Print clock and room
def clock_room(draw):
    j = 5
    # Print Room
    if s.seconde % 2 != 0:
        i = 116

        for c in s.room_current[:3]:
            legacy.text(draw, (i, j), chr(s.letter[c]), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_FONT)
            i += 4

    # Print Clock
    else:
        i = 108

        for c in s.now:
            legacy.text(draw, (i, j), chr(s.letter[c]), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_FONT)
            i += 4

# Print distance
def distance(draw):
    d = l.calc_distance(s.message[1], s.latitude, s.longitude)
    j = 18

    if d is False:
        d = 'NO LOC'
    else:
        d = str(d)

    i = 128 - len(d) * 4

    for c in d:
        legacy.text(draw, (i, j), chr(s.letter[c]), fill=get_color('screen', 'foreground'), font=s.SMALL_BITMAP_FONT)
        i += 4


# Print System Log Extended
def extended_system(draw, page):
    if s.device.height == 128:
        draw.rectangle((0, 1, s.device.height - 1, 13), fill=get_color('header', 'background'))

    legacy.text(draw, (0, 1), chr(0) + chr(1), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_CPU)
    legacy.text(draw, (0, 9), chr(2) + chr(3), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_CPU)

    w, h = draw.textsize(text='Infos Spotnik', font=font)
    tab = (s.device.width - w) / 2
    draw.text((tab, 4), 'Infos Spotnik', font=font, fill=get_color('header', 'foreground'))

    if page == 1:
        sys = {'Arch': '', 'Kernel': '', 'Uptime': '', 'Load': '', 'Freq': ''}
        sys_order = ['Arch', 'Kernel', 'Uptime', 'Load', 'Freq']

        sys['Arch'] = l.system_info('arch')
        sys['Kernel'] = l.system_info('kernel')
        sys['Uptime'] = l.system_info('up')
        sys['Load'] = l.system_info('load')
        sys['Freq'] = l.system_info('freq') + ' MHz'

    elif page == 2:
        sys = {'IP': '', 'Temp': '', 'Mem': '', 'Disk': '', 'Version': ''}
        sys_order = ['IP', 'Temp', 'Mem', 'Disk', 'Version']

        sys['IP'] = l.system_info('ip')
        sys['Temp'] = l.system_info('temp') + ' C'

        percent, mem = l.system_info('mem')
        sys['Mem'] = percent + '% of ' + mem

        percent, disk = l.system_info('disk')
        sys['Disk'] = percent + ' of ' + disk
        sys['Version'] = s.version

    else:
        sys = {'Arch': '', 'Kernel': '', 'Uptime': '', 'Load': '', 'Freq': '', 'IP': '', 'Temp': '', 'Mem': '', 'Disk': '', 'Version': ''}
        sys_order = ['Arch', 'Kernel', 'Uptime', 'Load', 'Freq', 'IP', 'Temp', 'Mem', 'Disk', 'Version']
        
        sys['Arch'] = l.system_info('arch')
        sys['Kernel'] = l.system_info('kernel')
        sys['Uptime'] = l.system_info('up')
        sys['Load'] = l.system_info('load')
        sys['Freq'] = l.system_info('freq') + ' MHz'

        sys['IP'] = l.system_info('ip')
        sys['Temp'] = l.system_info('temp') + ' C'

        percent, mem = l.system_info('mem')
        sys['Mem'] = percent + '% of ' + mem

        percent, disk = l.system_info('disk')
        sys['Disk'] = percent + ' of ' + disk
        sys['Version'] = s.version

    if s.device.height == 128:
        i = 17
    else:
        i = 16

    for j in sys_order:
        label(draw, i, 42, get_color('label', 'background'), get_color('label', 'foreground'), j, sys[j])
        if s.device.height == 128:
            i += 11
        else:
            i += 10

# Print Call Log Extended
def extended_call(draw, limit = 5):
    if s.device.height == 128:
        draw.rectangle((0, 1, s.device.height - 1, 13), fill=get_color('header', 'background'))

    legacy.text(draw, (0, 1), chr(0) + chr(1), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_CLOCK)
    legacy.text(draw, (0, 9), chr(2) + chr(3), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_CLOCK)

    w, h = draw.textsize(text='Derniers TX', font=font)
    tab = (s.device.width - w) / 2
    draw.text((tab, 4), 'Derniers TX', font=font, fill=get_color('header', 'foreground'))

    if s.device.height == 128:
        i = 17
    else:
        i = 16

    for j in xrange(0, limit):
        label(draw, i, 44, get_color('label', 'background'), get_color('label', 'foreground'), s.call_time[j], s.call[j])
        if s.device.height == 128:
            i += 11
        else:
            i += 10

# Print Best Log Extended
def extended_best(draw, limit = 5):
    if s.device.height == 128:
        draw.rectangle((0, 1, s.device.height - 1, 13), fill=get_color('header', 'background'))

    legacy.text(draw, (0, 1), chr(0) + chr(1), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_STAT)
    legacy.text(draw, (0, 9), chr(2) + chr(3), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_STAT)

    w, h = draw.textsize(text='Top links', font=font)
    tab = (s.device.width - w) / 2
    draw.text((tab, 4), 'Top links', font=font, fill=get_color('header', 'foreground'))

    best_min = min(s.best_time)
    best_max = max(s.best_time)

    if s.device.height == 128:
        i = 17
    else:
        i = 16

    for j in xrange(0, limit):
        c = s.best[j]
        n = int(s.best_time[j])

        if n == 0:
            break

        t = l.interpolation(n, best_min, best_max, 28, 42)
        if t == 0:
            t = 42

        label(draw, i, t, get_color('label', 'background'), get_color('label', 'foreground'), l.convert_second_to_time(n), c, 54)
        if s.device.height == 128:
            i += 11
        else:
            i += 10

# Print config
def extended_config(draw, page):
    if s.device.height == 128:
        draw.rectangle((0, 1, s.device.height - 1, 13), fill=get_color('header', 'background'))

    draw.text((2, 0), u'\ue800', font=icon, fill=get_color('header', 'foreground'))

    w, h = draw.textsize(text='Config Tracker', font=font)
    tab = (s.device.width - w) / 2
    draw.text((tab, 4), 'Config Tracker', font=font, fill=get_color('header', 'foreground'))

    if page == 1:
        sys = {'I2C Port': '', 'I2C Address': '', 'Display': '', 'Width': '', 'Height': ''}
        sys_order = ['I2C Port', 'I2C Address', 'Display', 'Width', 'Height']

        sys['I2C Port'] = str(s.i2c_port)
        sys['I2C Address'] = hex(s.i2c_address)
        sys['Display'] = s.display
        sys['Width'] = str(s.display_width)
        sys['Height'] = str(s.display_height)

    elif page == 2:
        sys = {'Scan': '', 'Follow': '', 'Indicatif': '', 'Latitude': '', 'Longitude': ''}
        sys_order = ['Scan', 'Follow', 'Indicatif', 'Latitude', 'Longitude']

        sys['Scan'] = str(s.scan)
        sys['Follow'] = str(s.follow)
        sys['Indicatif'] = s.callsign
        sys['Latitude'] = str(s.latitude)
        sys['Longitude'] = str(s.longitude)

    else:
        sys = {'I2C Port': '', 'I2C Address': '', 'Display': '', 'Width': '', 'Height': '', 'Scan': '', 'Follow': '', 'Indicatif': '', 'Latitude': '', 'Longitude': ''}
        sys_order = ['I2C Port', 'I2C Address', 'Display', 'Width', 'Height', 'Scan', 'Follow', 'Indicatif', 'Latitude', 'Longitude']
        
        sys['I2C Port'] = str(s.i2c_port)
        sys['I2C Address'] = hex(s.i2c_address)
        sys['Display'] = s.display
        sys['Width'] = str(s.display_width)
        sys['Height'] = str(s.display_height)

        sys['Scan'] = str(s.scan)
        sys['Follow'] = str(s.follow)
        sys['Indicatif'] = s.callsign
        sys['Latitude'] = str(s.latitude)
        sys['Longitude'] = str(s.longitude)

    if s.device.height == 128:
        i = 17
    else:
        i = 16

    for j in sys_order:
        label(draw, i, 63, get_color('label', 'background'), get_color('label', 'foreground'), j, sys[j])
        if s.device.height == 128:
            i += 11
        else:
            i += 10

# Print config
def extended_propagation(draw, page):
    if s.device.height == 128:
        draw.rectangle((0, 1, s.device.height - 1, 13), fill=get_color('header', 'background'))

    draw.text((2, 0), u'\ue803', font=icon, fill=get_color('header', 'foreground'))

    w, h = draw.textsize(text='Propagation', font=font)
    tab = (s.device.width - w) / 2
    draw.text((tab, 4), 'Propagation', font=font, fill=get_color('header', 'foreground'))

    if page == 1:
        value = {'Updated': '', 'Solar Flux': '', 'A-Index': '', 'K-Index': '', 'Sun Spots': ''}
        value_order = ['Updated', 'Solar Flux', 'A-Index', 'K-Index', 'Sun Spots']

        value['Updated'] = s.solar_value['Updated']
        value['Solar Flux'] = s.solar_value['Solar Flux']
        value['A-Index'] = s.solar_value['A-Index']
        value['K-Index'] = s.solar_value['K-Index']
        value['Sun Spots'] = s.solar_value['Sun Spots']
        
    elif page == 2:
        value = {'X-Ray': '', 'Ptn Flux': '', 'Elc Flux': '', 'Mag (BZ)': '', 'Solar Wind': ''}
        value_order = ['X-Ray', 'Ptn Flux', 'Elc Flux', 'Mag (BZ)', 'Solar Wind']

        value['X-Ray'] = s.solar_value['X-Ray']
        value['Ptn Flux'] = s.solar_value['Ptn Flux']
        value['Elc Flux'] = s.solar_value['Elc Flux']
        value['Mag (BZ)'] = s.solar_value['Mag (BZ)']
        value['Solar Wind'] = s.solar_value['Solar Wind']

    elif page == 3:
        value = {'Updated': '', 'Solar Flux': '', 'A-Index': '', 'K-Index': '', 'Sun Spots': '', 'X-Ray': '', 'Ptn Flux': '', 'Elc Flux': '', 'Mag (BZ)': '', 'Solar Wind': ''}
        value_order = ['Updated', 'Solar Flux', 'A-Index', 'K-Index', 'Sun Spots', 'X-Ray', 'Ptn Flux', 'Elc Flux', 'Mag (BZ)', 'Solar Wind']
        
        value['Updated'] = s.solar_value['Updated']
        value['Solar Flux'] = s.solar_value['Solar Flux']
        value['A-Index'] = s.solar_value['A-Index']
        value['K-Index'] = s.solar_value['K-Index']
        value['Sun Spots'] = s.solar_value['Sun Spots']

        value['X-Ray'] = s.solar_value['X-Ray']
        value['Ptn Flux'] = s.solar_value['Ptn Flux']
        value['Elc Flux'] = s.solar_value['Elc Flux']
        value['Mag (BZ)'] = s.solar_value['Mag (BZ)']
        value['Solar Wind'] = s.solar_value['Solar Wind']

        position = 50

    elif page == 4:
        value = {'80m-40m J/N': '', '30m-20m J/N': '', '17m-15m J/N': '', '12m-10m J/N': '', 'VHF Aurora': '', 'E-Skip EU 2m': '', 'E-Skip EU 4m': '', 'E-Skip EU 6m': '', 'Geomag Field': '', 'Signal Noise': ''}
        value_order = ['80m-40m J/N', '30m-20m J/N', '17m-15m J/N', '12m-10m J/N', 'VHF Aurora', 'E-Skip EU 2m', 'E-Skip EU 4m', 'E-Skip EU 6m', 'Geomag Field', 'Signal Noise']
        
        value['80m-40m J/N'] = s.solar_value['80m-40m Day'] + ' / ' + s.solar_value['80m-40m Night']
        value['30m-20m J/N'] = s.solar_value['30m-20m Day'] + ' / ' + s.solar_value['30m-20m Night']
        value['17m-15m J/N'] = s.solar_value['17m-15m Day'] + ' / ' + s.solar_value['17m-15m Night']
        value['12m-10m J/N'] = s.solar_value['12m-10m Day'] + ' / ' + s.solar_value['12m-10m Night']
        value['VHF Aurora'] = s.solar_value['VHF Aurora']

        value['E-Skip EU 2m'] = s.solar_value['E-Skip EU 2m']
        value['E-Skip EU 4m'] = s.solar_value['E-Skip EU 4m']
        value['E-Skip EU 6m'] = s.solar_value['E-Skip EU 6m']
        value['Geomag Field'] = s.solar_value['Geomag Field']
        value['Signal Noise'] = s.solar_value['Signal Noise']

        position = 60

    if s.device.height == 128:
        i = 17
    else:
        i = 16

    for j in value_order:
        label(draw, i, position, get_color('label', 'background'), get_color('label', 'foreground'), j, value[j])
        if s.device.height == 128:
            i += 11
        else:
            i += 10

# Print display on 128 x 64
def display_64():
    with canvas(s.device) as draw:
        draw.rectangle((0, 0, 127, s.device.height - 1), fill=get_color('screen', 'background'))
        draw.rectangle((0, 1, 127, 13), fill=get_color('header', 'background'))

        for i in xrange(0, 128, 2):
            draw.point((i,  0), fill=get_color('header', 'border'))
            draw.point((i, 14), fill=get_color('header', 'border'))

        # System log extended Page 1
        if s.transmit is False and s.minute % 2 == 0 and s.seconde < 5:
            extended_system(draw, 1)

        # System log extended Page 2
        elif s.transmit is False and s.minute % 2 == 0 and s.seconde < 10:
            extended_system(draw, 2)

        # Config log extended Page 1
        elif s.transmit is False and s.minute % 2 == 0 and s.seconde < 15:
            extended_config(draw, 1)

        # Config log extended Page 2
        elif s.transmit is False and s.minute % 2 == 0 and s.seconde < 20:
            extended_config(draw, 2)

        # Call log extended
        elif s.transmit is False and len(s.call) >=5 and s.minute % 2 == 0 and s.seconde < 30:
            extended_call(draw, len(s.call))

        # Best log extended
        elif s.transmit is False and len(s.best) >= 5 and s.minute % 2 == 0 and s.seconde < 40:
            extended_best(draw, len(s.call))

        # If not extended
        else:
            for i in xrange(0, 128, 2):     # Horizontal
                draw.point((i, 40), fill=get_color('screen', 'border'))    # Zone haut | Zone Histogramme - TOT

            if 'Dernier' in s.message[0]:   # Icon clock (DIY...)
                legacy.text(draw, (0, 1), chr(0) + chr(1), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_CLOCK)
                legacy.text(draw, (0, 9), chr(2) + chr(3), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_CLOCK)
            else:   # Icon stat
                legacy.text(draw, (0, 1), chr(0) + chr(1), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_STAT)
                legacy.text(draw, (0, 9), chr(2) + chr(3), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_STAT)

            # Icon talk
            if s.transmit is True:
                draw.text((2, 21), u'\uf130', font=icon, fill=get_color('tot', 'text'))
                distance(draw)

            # Print data
            i = 4
            j = 0

            for m in s.message:
                if m is not None:
                    w, h = draw.textsize(text=m, font=font)
                    tab = (s.device.width - w) / 2
                    vide = ' ' * 22     # Hack to speed clear screen line...
                    if j == 0:
                        color = get_color('header', 'foreground')
                    if j == 1:
                        color = get_color('log', 'call')
                    else:
                        color = get_color('log', 'call')

                    draw.text((0, i), vide, font=font, fill=get_color('header', 'foreground'))
                    draw.text((tab, i), m, font=font, fill=color)
                    if j > 0:
                        legacy.text(draw, (16, i + 1), chr(s.letter[str(j)]), font=s.SMALL_BITMAP_FONT, fill=color)

                    i += h
                    if i == 12:
                        i = 16
                    j += 1

            if s.transmit is True and s.duration > 0:
                # Draw tot
                tot(draw, legacy, s.duration, 57)
            else:
                # Draw stats histogram
                histogram(draw, legacy, 57)

        # Finaly, print clock and room
        clock_room(draw)

# Print display on 128 x 128 
def display_128():
    with canvas(s.device, dither=True) as draw:
        draw.rectangle((0, 0, 127, s.device.height - 1), fill=get_color('screen', 'background'))
        draw.rectangle((0, 1, 127, 13), fill=get_color('header', 'background'))

        for i in xrange(0, 128, 1):
            draw.point((i, 0), fill=get_color('header', 'border'))
            draw.point((i, 14), fill=get_color('header', 'border'))

        # System log extended
        if s.transmit is False and s.minute % 2 == 0 and s.seconde < 10:
            extended_system(draw, 3)

        # Config log extended
        elif s.transmit is False and s.minute % 2 == 0 and s.seconde < 20:
            extended_config(draw, 3)

        # Call log extended
        elif s.transmit is False and len(s.call) >=5 and s.minute % 2 == 0 and s.seconde < 30:
            extended_call(draw, len(s.call))

        # Best log extended
        elif s.transmit is False and len(s.best) >= 5 and s.minute % 2 == 0 and s.seconde < 40:
            extended_best(draw, len(s.best))

        # Propag extended
        elif s.transmit is False and  s.minute % 2 == 0 and s.seconde < 50:
            extended_propagation(draw, 3)
    
        elif s.transmit is False and  s.minute % 2 == 0 and s.seconde >= 50:
            extended_propagation(draw, 4)

        # If not extended
        else:
            for i in xrange(0, 128, 2):     # Horizontal
                draw.point((i, 40), fill=get_color('screen', 'border'))    # Zone haut | Zone Histogramme - TOT

            if 'Dernier' in s.message[0]:   # Icon clock (DIY...)
                legacy.text(draw, (0, 1), chr(0) + chr(1), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_CLOCK)
                legacy.text(draw, (0, 9), chr(2) + chr(3), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_CLOCK)
            else:   # Icon stat
                legacy.text(draw, (0, 1), chr(0) + chr(1), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_STAT)
                legacy.text(draw, (0, 9), chr(2) + chr(3), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_STAT)

            # Icon talk
            if s.transmit is True:
                draw.text((2, 21), u'\uf130', font=icon, fill=get_color('tot', 'foreground'))
                distance(draw)

            # Print data
            i = 4
            j = 0

            for m in s.message:
                if m is not None:
                    w, h = draw.textsize(text=m, font=font)
                    tab = (s.device.width - w) / 2
                    vide = ' ' * 22     # Hack to speed clear screen line...
                    if j == 0:
                        color = get_color('header', 'foreground')
                    elif j == 1:
                        color = get_color('log', 'call_last')
                    else:
                        color = get_color('log', 'call')

                    draw.text((0, i), vide, font=font, fill=get_color('header', 'background'))
                    draw.text((tab, i), m, font=font, fill=color)
                    if j > 0:
                        legacy.text(draw, (16, i + 1), chr(s.letter[str(j)]), font=s.SMALL_BITMAP_FONT, fill=color)
                        if s.transmit is False:
                            k = 108
                            for c in s.call_time[j - 1]:
                                legacy.text(draw, (k, i + 1), chr(s.letter[c]), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_FONT)
                                k += 4

                    i += h
                    if i == 12:
                        i = 16
                    j += 1

            if s.transmit is True and s.duration > 0:
                # Draw tot
                tot(draw, legacy, s.duration, 69)
                if s.duration < 10:
                    # Whois
                    whois(draw)
                else:
                    # Elsewhere
                    elsewhere(draw, s.raptor)
            else:
                # Draw stats histogram
                histogram(draw, legacy, 69, 28)
                # Elsewhere
                elsewhere(draw, s.raptor)

        # Finaly, print clock and room
        clock_room(draw)