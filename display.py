#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
RRFDisplay version Raspberry Pi 3B et Orange Pi Zero
Learn more about RRF on https://f5nlg.wordpress.com
Check video about RRFDisplay on https://www.youtube.com/watch?v=rVW8xczVpEo
73 & 88 de F4HWN Armel
'''

import settings as s
import lib as l
import time
import os

from luma.core.render import canvas
from luma.core import legacy

from PIL import ImageFont

'''
with canvas(s.device, dither=True) as draw:
    if s.device.height > 160:
        icon = ImageFont.truetype('./fonts/fontello.ttf', 14)     # Icon font
        font = ImageFont.truetype('./fonts/7x5.ttf', 8)           # Text font
    else:
        icon = ImageFont.truetype('./fonts/fontello.ttf', 14)     # Icon font
        font = ImageFont.truetype('./fonts/freepixel.ttf', 16)    # Text font

    font_big = ImageFont.truetype('./fonts/bold.ttf', 30)     # Text font
    font_tot = ImageFont.truetype('./fonts/rounded_led_board.ttf', 20)    # Text font
'''

icon = ImageFont.truetype('./fonts/fontello.ttf', 14)     # Icon font
font = ImageFont.truetype('./fonts/7x5.ttf', 8)           # Text font
font_big = ImageFont.truetype('./fonts/bold.ttf', 30)     # Text font
font_tot = ImageFont.truetype('./fonts/rounded_led_board.ttf', 20)    # Text font

# Manage color
def get_color(section, value):
    color = s.theme.get(section, value)
    if color in s.color:
        return s.color[color]
    else:
        return color

# Draw title
def title(draw, message, width=0, offset=0):
    if width == 0:
        width = s.device.width
    w, h = draw.textsize(text=message, font=font)
    tab = (width - w) / 2
    draw.text((tab + offset, 4), message, font=font, fill=get_color('header', 'foreground'))

# Draw last call
def last(draw, call, width=0, offset=0):
    if width == 0:
        width = s.device.width
    # Print last_call
    i = 16
    j = 1

    for c in call:
        if c is not '':
            w, h = draw.textsize(text=c, font=font)
            tab = (width - w) / 2
            if j == 1:
                color = get_color('log', 'call_last')
            else:
                color = get_color('log', 'call')

            draw.text((tab + offset, i), c, font=font, fill=color)
            legacy.text(draw, (16 + offset, i + 1), chr(s.letter[str(j)]), font=s.SMALL_BITMAP_FONT, fill=color)
            if s.transmit is False:
                k = 108
                for l in s.call_time[j - 1][:5]:
                    legacy.text(draw, (k + offset, i + 1), chr(s.letter[l]), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_FONT)
                    k += 4

            i += h
            j += 1

# Draw label

#label(draw, i, 42, get_color('label', 'background'), get_color('label', 'foreground'), s.iptable[j], s.iptable_by[j], 0, offset)

def label(draw, position, width, bg_color, fg_color, label, value, fixed=0, offset=0):
    if s.device.height >= 128:
        position += 3
        draw.rectangle((0 + offset, position - 1, width + offset, position + 8), fill=bg_color)
        draw.line((width + offset + 1, position, width + offset + 1, position + 7), fill=bg_color)
        draw.line((width + offset + 2, position + 1, width + offset + 2, position + 6), fill=bg_color)
        draw.line((width + offset + 3, position + 2, width + offset + 3, position + 5), fill=bg_color)
        draw.line((width + offset + 4, position + 3, width + offset + 4, position + 4), fill=bg_color)
    else:
        draw.rectangle((0 + offset, position - 1, width + offset, position + 7), fill=bg_color)
        draw.line((width + offset + 1, position, width + offset + 1, position + 6), fill=bg_color)
        draw.line((width + offset + 2, position + 1, width + offset + 2, position + 5), fill=bg_color)
        draw.line((width + offset + 3, position + 2, width + offset + 3, position + 4), fill=bg_color)
        draw.line((width + offset + 4, position + 3, width + offset + 4, position + 3), fill=bg_color)
        #draw.point((width + 4, position + 4), fill=bg_color)

    draw.text((1 + offset, position), label, font=font, fill=fg_color)
    if fixed == 0:
        draw.text((width + offset + 10, position), value, font=font, fill=get_color('screen', 'foreground'))
    else:
        draw.text((fixed + offset, position), value, font=font, fill=get_color('screen', 'foreground'))        

# Draw tot
def tot(draw, legacy, duration, position, width=0, offset=0):
    if width == 0:
        width = s.device.width
    #duration += (duration / 60)     # Reajust time latence
    if s.device.height < 128:
        j = 54
        k = 11

        duration_min = 0

        timer = [i for i in range(60, 360, 60)]

        for i in timer:
            if duration < i:
                duration_max = i
                break
            else:
                duration_min = i

        h = l.interpolation(duration, duration_min, duration_max, 0, 120)

        draw.rectangle((0, j, 128, j - k), fill=get_color('screen', 'background'))
        for i in range(3, h, 2):
            draw.rectangle((i, j, i, j - k), fill=get_color('screen', 'foreground'))

        for i in range(0, 128, 4):
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
        tmp = l.convert_second_to_time(duration)
        w, h = draw.textsize(text=tmp, font=font_tot)
        tab = (width - w) / 2
        draw.text((tab + offset, 57), tmp, font=font_tot, fill=get_color('screen', 'foreground'))

# Print elsewhere
def elsewhere(draw, data, offset=0):
    draw.rectangle((0 + offset, 77, 127 + offset, 127), outline=get_color('elsewhere', 'border'), fill=get_color('elsewhere', 'background'))

    # Horizontal

    for i in [87, 97, 107, 117]:
        draw.line((0 + offset,  i, 127 + offset,  i), fill=get_color('elsewhere', 'border'))

    i = 79
    for d in data:
        d = d.split('/')

        if d[0] == '00:00':
            draw.rectangle((21 + offset, i - 1, 126 + offset, i + 7), fill=get_color('elsewhere', 'background'))
            if 'h' in d[2]:
                draw.text((28 + offset, i), d[2], font=font, fill=get_color('elsewhere', 'foreground'))
            else:
                draw.text((48 + offset, i), d[2], font=font, fill=get_color('elsewhere', 'foreground'))

            draw.text((100 + offset, i), d[3], font=font, fill=get_color('elsewhere', 'foreground'))
        else:
            draw.rectangle((21 + offset, i - 1, 126 + offset, i + 7), fill=get_color('elsewhere', 'background_active'))
            draw.text((28 + offset, i), d[2], font=font, fill=get_color('elsewhere', 'foreground_active'))
            draw.text((100 + offset, i), d[3], font=font, fill=get_color('elsewhere', 'foreground_active'))

        draw.rectangle((1 + offset, i - 1, 19 + offset, i + 7), fill=get_color('elsewhere', 'background_active'))
        draw.text((2 + offset, i), d[1], font=font, fill=get_color('elsewhere', 'foreground_active'))

        i += 10

    # Vertical

    draw.line((20 + offset, 77, 20 + offset, 127), fill=get_color('elsewhere', 'border'))
    draw.line((94 + offset, 77, 94 + offset, 127), fill=get_color('elsewhere', 'border'))

# Print whois
def whois(draw, offset=0):
    draw.rectangle((0 + offset, 77, 127 + offset, 127), outline=get_color('whois', 'border'), fill=get_color('whois', 'background'))
    draw.rectangle((1 + offset, 78,  47 + offset, 126), fill=get_color('whois', 'background_active'))

    # Vertical

    draw.line((48 + offset, 77,  48 + offset, 127), fill=get_color('whois', 'border'))

    # Horizontal

    for i in [87, 97, 107, 117]:
        draw.line((0 + offset,  i, 127 + offset,  i), fill=get_color('whois', 'border'))

    draw.text((2 + offset, 79), 'Type', font=font, fill=get_color('whois', 'foreground_active'))
    draw.text((50 + offset, 79), s.call_type, font=font, fill=get_color('whois', 'foreground'))

    draw.text((2 + offset, 89), 'Detail', font=font, fill=get_color('whois', 'foreground_active'))
    if len(s.call_description) > 14:
        draw.text((50 + offset, 89), s.call_description[:14] + '...', font=font, fill=get_color('whois', 'foreground'))
    else:
        draw.text((50 + offset, 89), s.call_description, font=font, fill=get_color('whois', 'foreground'))

    draw.text((2 + offset, 99), 'Tone', font=font, fill=get_color('whois', 'foreground_active'))
    draw.text((50 + offset, 99), s.call_tone, font=font, fill=get_color('whois', 'foreground'))

    draw.text((2 + offset, 109), 'Locator', font=font, fill=get_color('whois', 'foreground_active'))
    draw.text((50 + offset, 109), s.call_locator, font=font, fill=get_color('whois', 'foreground'))

    if s.call_sysop == '':
        if s.call_prenom != '':
            draw.text((2 + offset, 119), 'Prenom', font=font, fill=get_color('whois', 'foreground_active'))
            draw.text((50 + offset, 119), s.call_prenom, font=font, fill=get_color('whois', 'foreground'))
        else:
            draw.text((2 + offset, 119), 'Sysop', font=font, fill=get_color('whois', 'foreground_active'))
            draw.text((50 + offset, 119), s.call_sysop, font=font, fill=get_color('whois', 'foreground'))
    else:
        draw.text((2 + offset, 119), 'Sysop', font=font, fill=get_color('whois', 'foreground_active'))
        draw.text((50 + offset, 119), s.call_sysop, font=font, fill=get_color('whois', 'foreground'))

# Draw histogram
def histogram(draw, legacy, position, height=15, offset=0):
    qso_hour_max = max(s.qso_hour)

    i = 5
    j = 100

    for (t, q) in enumerate(s.qso_hour):
        if q != 0:
            h = l.interpolation(q, 0, qso_hour_max, 0, height)
        else:
            h = 0

        draw.rectangle((0 + offset + i, position, i + offset + 2, (position - height)), fill=get_color('screen', 'background'))
        if t == s.hour:
            color = get_color('histogram', 'column_current')
        else:
            color = get_color('histogram', 'column')

        draw.rectangle((0 + offset + i, position, i + offset + 2, (position - h)), fill=color)
        
        j += 5
        i += 5

    for i, j, k in [(1, 0, 0), (33, 0, 6), (63, 1, 2), (93, 1, 8), (120, 2, 3)]:
        legacy.text(draw, (i + offset, position + 2), chr(j) + chr(k), fill=get_color('histogram', 'legend'), font=s.SMALL_BITMAP_FONT)

# Print clock and room
def clock_room(draw, offset=0):
    j = 5
    # Print Room
    if s.seconde % 5 != 0:
        i = 116

        for c in s.room_current[:3]:
            legacy.text(draw, (i + offset, j), chr(s.letter[c]), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_FONT)
            i += 4

    # Print Clock
    else:
        i = 108

        for c in s.now[:5]:
            legacy.text(draw, (i + offset, j), chr(s.letter[c]), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_FONT)
            i += 4

# Print distance
def distance(draw, offset=0):
    d = l.calc_distance(s.message[1], s.latitude, s.longitude)
    j = 18

    if d is False:
        d = 'NO LOC'
    else:
        d = str(d)

    i = 128 - len(d) * 4

    for c in d:
        legacy.text(draw, (i + offset, j), chr(s.letter[c]), fill=get_color('screen', 'foreground'), font=s.SMALL_BITMAP_FONT)
        i += 4


# Print System Log Extended
def extended_system(draw, page, width=0, offset=0):
    if width == 0:
        width = s.device.width

    legacy.text(draw, (0 + offset, 1), chr(0) + chr(1), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_CPU)
    legacy.text(draw, (0 + offset, 9), chr(2) + chr(3), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_CPU)

    title(draw, 'Infos Spotnik', width, offset)

    if page == 1:
        sys = {'Arch': '', 'Kernel': '', 'Uptime': '', 'Load': '', 'Freq': ''}
        sys_order = ['Arch', 'Kernel', 'Uptime', 'Load', 'Freq']

    elif page == 2:
        sys = {'IP': '', 'Temp': '', 'Mem': '', 'Disk': '', 'Version': ''}
        sys_order = ['IP', 'Temp', 'Mem', 'Disk', 'Version']

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

    i = 15

    for j in sys_order:
        label(draw, i, 42, get_color('label', 'background'), get_color('label', 'foreground'), j, sys[j], 0, offset)
        if s.device.height >= 128:
            i += 11
        else:
            i += 10

# Print Call Log Extended
def extended_call(draw, limit = 5, width=0, offset=0):
    if width == 0:
        width = s.device.width

    legacy.text(draw, (0 + offset, 1), chr(0) + chr(1), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_CLOCK)
    legacy.text(draw, (0 + offset, 9), chr(2) + chr(3), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_CLOCK)

    title(draw, 'Derniers TX', width, offset)

    i = 15

    for j in range(0, limit):
        label(draw, i, 42, get_color('label', 'background'), get_color('label', 'foreground'), s.call_time[j], s.call[j], 0, offset)
        if s.device.height >= 128:
            i += 11
        else:
            i += 10

# Print Iptable Log Extended
def extended_iptable(draw, limit = 5, width=0, offset=0):
    if width == 0:
        width = s.device.width

    #legacy.text(draw, (160 + offset, 1), chr(0) + chr(1), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_STAT)
    #legacy.text(draw, (160 + offset, 9), chr(2) + chr(3), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_STAT)

    #title(draw, 'Iptable', width, offset)

    draw.line((0 + offset, 157, 127 + offset, 157), fill=get_color('header', 'border'))

    i = 160

    for j in range(0, limit):
        if s.iptable[j] == '':
            break
        label(draw, i, 65, get_color('label', 'background'), get_color('label', 'foreground'), s.iptable[j], s.iptable_by[j], 0, offset)
        if s.device.height >= 128:
            i += 11
        else:
            i += 10

# Print Best Log Extended
def extended_best(draw, limit = 5, width=0, offset=0):
    if width == 0:
        width = s.device.width

    legacy.text(draw, (0 + offset, 1), chr(0) + chr(1), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_STAT)
    legacy.text(draw, (0 + offset, 9), chr(2) + chr(3), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_STAT)

    title(draw, 'Top links', width, offset)

    best_min = min(s.best_time)
    best_max = max(s.best_time)

    i = 15

    for j in range(0, limit):
        c = s.best[j]
        n = int(s.best_time[j])

        if n == 0:
            break

        t = l.interpolation(n, best_min, best_max, 28, 42)
        if t == 0:
            t = 42

        label(draw, i, t, get_color('label', 'background'), get_color('label', 'foreground'), l.convert_second_to_time(n), c, 54, offset)
        if s.device.height >= 128:
            i += 11
        else:
            i += 10

# Print config
def extended_config(draw, page, width=0, offset=0):
    if width == 0:
        width = s.device.width

    draw.text((2 + offset, 0), '\ue800', font=icon, fill=get_color('header', 'foreground'))

    title(draw, 'Config Display', width, offset)

    if page == 1:
        sys = {'I2C Port': '', 'I2C Address': '', 'Display': '', 'Width': '', 'Height': ''}
        sys_order = ['I2C Port', 'I2C Address', 'Display', 'Width', 'Height']

    elif page == 2:
        sys = {'Scan': '', 'Follow': '', 'Refresh': '', 'Latitude': '', 'Longitude': ''}
        sys_order = ['Scan', 'Follow', 'Refresh', 'Latitude', 'Longitude']

    else:
        sys = {'I2C Port': '', 'I2C Address': '', 'Display': '', 'Width': '', 'Height': '', 'Scan': '', 'Follow': '', 'Refresh': '', 'Latitude': '', 'Longitude': ''}
        sys_order = ['I2C Port', 'I2C Address', 'Display', 'Width', 'Height', 'Scan', 'Follow', 'Refresh', 'Latitude', 'Longitude']
        
    sys['I2C Port'] = str(s.i2c_port)
    sys['I2C Address'] = hex(s.i2c_address)
    if 'frame' in s.display:
        sys['Display'] = '/dev/fb0'
    else:
        sys['Display'] = s.display    
    sys['Width'] = str(s.display_width)
    sys['Height'] = str(s.display_height)
    sys['Scan'] = str(s.scan)
    if s.scan is True:
        sys['Follow'] = s.callsign
    else:
        sys['Follow'] = s.room_current
    sys['Refresh'] = str(s.refresh) + 's'
    sys['Latitude'] = str(s.latitude)
    sys['Longitude'] = str(s.longitude)

    i = 15

    for j in sys_order:
        label(draw, i, 63, get_color('label', 'background'), get_color('label', 'foreground'), j, sys[j], 0, offset)
        if s.device.height >= 128:
            i += 11
        else:
            i += 10

# Print solar propagation
def extended_solar(draw, page, width=0, offset=0):
    if width == 0:
        width = s.device.width

    draw.text((2 + offset, 0), '\ue803', font=icon, fill=get_color('header', 'foreground'))

    title(draw,'Propagation', width, offset)

    if len(s.solar_value) != 0:
        if page == 1:
            value = {'Updated': '', 'Solar Flux': '', 'A-Index': '', 'K-Index': '', 'Sun Spots': ''}
            value_order = ['Updated', 'Solar Flux', 'A-Index', 'K-Index', 'Sun Spots']
            
        elif page == 2:
            value = {'X-Ray': '', 'Ptn Flux': '', 'Elc Flux': '', 'Mag (BZ)': '', 'Solar Wind': ''}
            value_order = ['X-Ray', 'Ptn Flux', 'Elc Flux', 'Mag (BZ)', 'Solar Wind']

        elif page == 3:
            value = {'Updated': '', 'Solar Flux': '', 'A-Index': '', 'K-Index': '', 'Sun Spots': '', 'X-Ray': '', 'Ptn Flux': '', 'Elc Flux': '', 'Mag (BZ)': '', 'Solar Wind': ''}
            value_order = ['Updated', 'Solar Flux', 'A-Index', 'K-Index', 'Sun Spots', 'X-Ray', 'Ptn Flux', 'Elc Flux', 'Mag (BZ)', 'Solar Wind']
            
        else:
            value = {'80m-40m J/N': '', '30m-20m J/N': '', '17m-15m J/N': '', '12m-10m J/N': '', 'VHF Aurora': '', 'E-Skip EU 2m': '', 'E-Skip EU 4m': '', 'E-Skip EU 6m': '', 'Geomag Field': '', 'Signal Noise': ''}
            value_order = ['80m-40m J/N', '30m-20m J/N', '17m-15m J/N', '12m-10m J/N', 'VHF Aurora', 'E-Skip EU 2m', 'E-Skip EU 4m', 'E-Skip EU 6m', 'Geomag Field', 'Signal Noise']
            
        if page <= 3:
            position = 50

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
        else:
            position = 60

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
        
        i = 15
        for j in value_order:
            label(draw, i, position, get_color('label', 'background'), get_color('label', 'foreground'), j, value[j], 0, offset)
            i += 11
    else:
        w, h = draw.textsize(text='No data', font=font)
        tab = (s.device.width - w) / 2
        draw.text((tab + offset, 17), 'No data', font=font, fill=get_color('screen', 'foreground'))

# Print display on 128 x 64
def display_init(init_message):
    with canvas(s.device) as draw:
        s.device.clear()
        draw.rectangle((0, 0, s.device.width - 1, s.device.height - 1), fill='white')

        position = 0
        for message in init_message:
            w, h = draw.textsize(text=message, font=font)
            tab = (s.device.width - w) / 2
            draw.text((tab, position), message, font=font, fill='white')
            position += 8

# Display gateway
def display_gateway(draw, offset=0):
    if s.device.height == 64:
        display_128_64(draw)
    elif s.device.height == 128:
        display_128_128(draw)
    elif s.device.height == 160:
        display_128_160(draw)
    elif s.device.height == 240:
        display_320_240(draw, offset)

# Print display on 128 x 64
def display_128_64(draw):
    with canvas(s.device) as draw:
        draw.rectangle((0, 0, 127, s.device.height - 1), fill=get_color('screen', 'background'))
        draw.rectangle((0, 1, 127, 13), fill=get_color('header', 'background'))

        for i in range(0, 128, 2):
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
            for i in range(0, 128, 2):     # Horizontal
                draw.point((i, 40), fill=get_color('screen', 'border'))    # Zone haut | Zone Histogramme - TOT

            if 'Dernier' in s.message[0]:   # Icon clock (DIY...)
                legacy.text(draw, (0, 1), chr(0) + chr(1), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_CLOCK)
                legacy.text(draw, (0, 9), chr(2) + chr(3), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_CLOCK)
            else:   # Icon stat
                legacy.text(draw, (0, 1), chr(0) + chr(1), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_STAT)
                legacy.text(draw, (0, 9), chr(2) + chr(3), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_STAT)

            # Icon talk
            if s.transmit is True:
                draw.text((2, 21), '\uf130', font=icon, fill=get_color('tot', 'text'))
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
                tot(draw, legacy, s.duration, 57)
            else:
                # Draw stats histogram
                histogram(draw, legacy, 57)

        # Finaly, print clock and room
        clock_room(draw)

# Print display on 128 x 128 
def display_128_128(draw, width=0, offset=0):
    if width == 0:
        width = s.device.width
    
    draw.rectangle((0 + offset, 0, 127 + offset, s.device.height - 1), fill=get_color('screen', 'background'))
    draw.rectangle((0 + offset, 1, 127 + offset, 13), fill=get_color('header', 'background'))

    draw.line((0 + offset, 0, 127 + offset, 0), fill=get_color('header', 'border'))
    draw.line((0 + offset, 14, 127 + offset, 14), fill=get_color('header', 'border'))

    if s.transmit is False and s.minute % 2 == 0:
        draw.rectangle((0 + offset, 1, 128 - 1 + offset, 13), fill=get_color('header', 'background'))

        # System log extended
        if s.seconde < 10:
            extended_system(draw, 3, width, offset)

        # Config log extended
        elif s.seconde < 20:
            extended_config(draw, 3, width, offset)

        # Call log extended
        elif s.seconde < 30 and len(s.call) >= 5:
            extended_call(draw, len(s.call), width, offset)

        # Best log extended
        elif s.seconde < 40 and len(s.best) >= 5:
            extended_best(draw, len(s.best), width, offset)

        # Propag extended
        elif s.seconde < 50:
            extended_solar(draw, 3, width, offset)
    
        elif s.seconde < 60:
            extended_solar(draw, 4, width, offset)
        
    # If not extended
    else:
        draw.rectangle((0 + offset, 15, 127 + offset, 40), fill=get_color('log', 'background'))
        draw.line((0 + offset, 40, 127 + offset, 40), fill=get_color('header', 'border'))

        if s.message[0] is not None and 'Dernier' in s.message[0]:   # Icon clock (DIY...)
            legacy.text(draw, (0 + offset, 1), chr(0) + chr(1), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_CLOCK)
            legacy.text(draw, (0 + offset, 9), chr(2) + chr(3), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_CLOCK)
        else:   # Icon stat
            legacy.text(draw, (0 + offset, 1), chr(0) + chr(1), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_STAT)
            legacy.text(draw, (0 + offset, 9), chr(2) + chr(3), fill=get_color('header', 'foreground'), font=s.SMALL_BITMAP_STAT)

        # Draw title
        title(draw, s.message[0], width, offset)

        # And after...            
        if s.transmit is False:
            # Draw message
            last(draw, s.message[1:], width, offset)
            # Draw stats histogram
            histogram(draw, legacy, 69, 28, offset)
            # Elsewhere
            elsewhere(draw, s.raptor, offset)

        elif s.transmit is True:
            # Draw tot
            tot(draw, legacy, s.duration, 69, width, offset)
            if s.duration < 10:
                # Draw call
                tmp = s.call_current.split(' ')
                if len(tmp) == 3:
                    tmp = tmp[1]
                else:
                    tmp = 'RTFM'

                w, h = draw.textsize(text=tmp, font=font_big)
                tab = (width - w) / 2
                draw.text((tab + offset, 14), tmp, font=font_big, fill=get_color('log', 'call_last'))
                # Whois
                whois(draw, offset)
            else:
                # Draw message
                last(draw, s.message[1:], width, offset)
                # Draw icon and distance
                draw.text((2 + offset, 21), '\uf130', font=icon, fill=get_color('tot', 'foreground'))
                distance(draw, offset)
                # Elsewhere
                elsewhere(draw, s.raptor, offset)

    # Finaly, print clock and room
    clock_room(draw, offset) 

# Print display on 128 x 160 
def display_128_160(draw, width=0, offset=0):
    if width == 0:
        width = s.device.width

    display_128_128(draw, width, offset)

    draw.line((0 + offset, 127, 127 + offset, 127), fill=get_color('header', 'border'))

    if s.transmit is True and s.duration >= 10:
        # Draw call
        tmp = s.call_current.split(' ')
        if len(tmp) == 3:
            tmp = tmp[1]
        else:
            tmp = 'RTFM'

        w, h = draw.textsize(text=tmp, font=font_big)
        tab = (width - w) / 2
        draw.text((tab + offset, 130), tmp, font=font_big, fill=get_color('log', 'call_last'))
    else:
        if s.seconde < 30:
            tmp = s.now[0:5]
        else:
            tmp = s.room_current[0:3]

        w, h = draw.textsize(text=tmp, font=font_big)
        tab = (width - w) / 2
        draw.text((tab + offset, 130), tmp, font=font_big, fill=get_color('log', 'call_last'))

        if s.seconde < 30 and s.seconde % 2 == 0:
            draw.rectangle((58 + offset, 128, 64 + offset, 160), fill=get_color('screen', 'background'))

# Print display on 320 x 240
def display_320_240(draw, offset):
    '''
    if s.minute % 5 == 0 and s.seconde == 0:
        l.get_image()

    if s.minute % 2 != 0 and s.seconde > 50 and s.transmit is False:
        img_path = str(Path(__file__).resolve().parent.joinpath('data', 'greyline.jpg'))

        greyline = Image.open(img_path) \
            .transform(s.device.size, Image.AFFINE, (1, 0, 0, 0, 1, 0), Image.BILINEAR) \
            .convert(s.device.mode)

        s.device.display(greyline)

        time.sleep(15)

    else:
        display_128_160(draw, 128, offset)
    '''
    display_128_160(draw, 128, offset)
    extended_iptable(draw, len(s.iptable), 128, offset)
