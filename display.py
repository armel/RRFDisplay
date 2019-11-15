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

from luma.core.render import canvas
from luma.core import legacy

from PIL import ImageFont

icon = ImageFont.truetype('fonts/fontello.ttf', 14)     # Icon font
font = ImageFont.truetype('fonts/7x5.ttf', 8)           # Text font
font_tot = ImageFont.truetype('fonts/astro.ttf', 50)    # Text font


# Draw tot
def tot(draw, legacy, duration, position):
    #duration += (duration / 60)     # Reajust time latence
    if s.device.height < 128:

        duration_min = 0

        timer = [i for i in xrange(60, 360, 60)]

        for i in timer:
            if duration < i:
                duration_max = i
                break
            else:
                duration_min = i

        h = l.interpolation(duration, duration_min, duration_max, 0, 120)

        draw.rectangle((0, 54, 128, 43), fill=s.color['black'])
        for i in xrange(3, h, 2):
            draw.rectangle((i, 54, i, 43), fill=s.color['white'])

        for i in xrange(0, 128, 4):
            draw.line((i, position, i + 1, position), fill=s.color['white'])

        # Duration min
        tmp = list(str(duration_min))
        msg = ''
        for c in tmp:
            msg += chr(s.letter[c])
        legacy.text(draw, (0, position + 2), msg, fill=s.color['white'], font=s.SMALL_BITMAP_FONT)

        # Duration max
        tmp = list(str(duration_max))
        msg = ''
        for c in tmp:
            msg += chr(s.letter[c])
        if duration_max < 100:
            tab = 4
        else:
            tab = 0
        legacy.text(draw, (115 + tab, position + 2), msg, fill=s.color['white'], font=s.SMALL_BITMAP_FONT)

        # duration
        tmp = list(str(duration))
        msg = ''
        for c in tmp:
            msg += chr(s.letter[c])
        if duration < 10:
            tab = 2
        else:
            tab = 0

        legacy.text(draw, (60 + tab, position + 2), msg, fill=s.color['white'], font=s.SMALL_BITMAP_FONT)
    else:
        if s.room_current == 'RRF':
            if duration > 90:
                color = s.color['white']
            elif duration > 60:
                color = s.color['silver']
            elif duration > 30:
                color = s.color['gray']
            else:
                color = s.color['dimgray']
        else:
            if duration > 240:
                color = s.color['white']
            elif duration > 120:
                color = s.color['silver']
            elif duration > 60:
                color = s.color['gray']
            else:
                color = s.color['dimgray']

        draw.text((8, 30), l.convert_second_to_time(duration), font=font_tot, fill=color)


# Draw histogram
def histogram(draw, legacy, position, height = 15):

    qso_hour_max = max(s.qso_hour)

    i = 5

    for q in s.qso_hour:
        if q != 0:
            h = l.interpolation(q, 0, qso_hour_max, 0, height)
        else:
            h = 0

        draw.rectangle((0 + i, position, i + 2, (position - height)), fill=s.color['black'])
        draw.rectangle((0 + i, position, i + 2, (position - h)), fill=s.color['dimgray'])
        i += 5

    legacy.text(draw, (1, position + 2), chr(0) + chr(0), fill=s.color['white'], font=s.SMALL_BITMAP_FONT)
    legacy.text(draw, (33, position + 2), chr(0) + chr(6), fill=s.color['white'], font=s.SMALL_BITMAP_FONT)
    legacy.text(draw, (63, position + 2), chr(1) + chr(2), fill=s.color['white'], font=s.SMALL_BITMAP_FONT)
    legacy.text(draw, (93, position + 2), chr(1) + chr(8), fill=s.color['white'], font=s.SMALL_BITMAP_FONT)
    legacy.text(draw, (120, position + 2), chr(2) + chr(3), fill=s.color['white'], font=s.SMALL_BITMAP_FONT)


# Print clock and room
def clock_room(draw):

    # Print Room
    if s.seconde %5 != 0:
        i = 116

        for c in s.room_current[:3]:
            legacy.text(draw, (i, 5), chr(s.letter[c]), fill=s.color['white'], font=s.SMALL_BITMAP_FONT)
            i += 4

    # Print Clock
    else:
        i = 108

        for c in s.now:
            legacy.text(draw, (i, 5), chr(s.letter[c]), fill=s.color['white'], font=s.SMALL_BITMAP_FONT)
            i += 4


# Print distance
def distance(draw):
    d = l.calc_distance(s.message[2], s.latitude, s.longitude)

    if d == 0:
        d = '---'
    else:
        d = str(d)

    i = 128 - len(d) * 4

    for c in d:
        legacy.text(draw, (i, 18), chr(s.letter[c]), fill=s.color['white'], font=s.SMALL_BITMAP_FONT)
        i += 4


# Print System Log Extended

def extended_system(draw, page):
    draw.rectangle((0, 15, 127, s.device.height - 1), fill=s.color['black'])
    legacy.text(draw, (0, -2), chr(0) + chr(1), fill=s.color['white'], font=s.SMALL_BITMAP_CPU)
    legacy.text(draw, (0, 6), chr(2) + chr(3), fill=s.color['white'], font=s.SMALL_BITMAP_CPU)

    w, h = draw.textsize(text='Infos Spotnik', font=font)
    tab = (s.device.width - w) / 2
    draw.text((tab, 4), 'Infos Spotnik', font=font, fill=s.color['white'])

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

    i = 24

    for j in sys_order:
        draw.rectangle((0, i - 1, 38, i + 7), fill=s.color['dimgray'])
        draw.line((39, i, 39, i + 6), fill=s.color['dimgray'])
        draw.line((40, i + 2, 40, i + 4), fill=s.color['dimgray'])
        draw.point((41, i + 3), fill=s.color['dimgray'])

        draw.text((1, i), j, font=font, fill=s.color['black'])
        draw.text((48, i), sys[j], font=font, fill=s.color['white'])

        i += 10

# Print Call Log Extended

def extended_call(draw, limit = 5):
    draw.rectangle((0, 15, 127, s.device.height - 1), fill=s.color['black'])
    legacy.text(draw, (0, -2), chr(0) + chr(1), fill=s.color['white'], font=s.SMALL_BITMAP_CLOCK)
    legacy.text(draw, (0, 6), chr(2) + chr(3), fill=s.color['white'], font=s.SMALL_BITMAP_CLOCK)

    w, h = draw.textsize(text='TX recents', font=font)
    tab = (s.device.width - w) / 2
    draw.text((tab, 4), 'TX recents', font=font, fill=s.color['white'])

    i = 24

    for j in xrange(0, limit):
        draw.rectangle((0, i - 1, 42, i + 7), fill=s.color['dimgray'])
        draw.line((43, i, 43, i + 6), fill=s.color['dimgray'])
        draw.line((44, i + 2, 44, i + 4), fill=s.color['dimgray'])
        draw.point((45, i + 3), fill=s.color['dimgray'])

        draw.text((1, i), s.call_time[j], font=font, fill=s.color['black'])
        draw.text((54, i), s.call[j], font=font, fill=s.color['white'])

        i += 10


# Print Best Log Extended

def extended_best(draw, limit = 5):
    draw.rectangle((0, 15, 127, s.device.height - 1), fill=s.color['black'])
    draw.text((0, 0), u'\ue801', font=icon, fill=s.color['white'])

    w, h = draw.textsize(text='Top links', font=font)
    tab = (s.device.width - w) / 2
    draw.text((tab, 4), 'Top links', font=font, fill=s.color['white'])

    best_min = min(s.best_time)
    best_max = max(s.best_time)

    i = 24

    for j in xrange(0, limit):
        c = s.best[j]
        n = int(s.best_time[j])

        if n == 0:
            break

        t = l.interpolation(n, best_min, best_max, 28, 42)
        if t == 0:
            t = 42

        draw.rectangle((0, i - 1, t, i + 7), fill=s.color['dimgray'])
        draw.line((t + 1, i, t + 1, i + 6), fill=s.color['dimgray'])
        draw.line((t + 2, i + 2, t + 2, i + 4), fill=s.color['dimgray'])
        draw.point((t + 3, i + 3), fill=s.color['dimgray'])

        draw.text((1, i), l.convert_second_to_time(n), font=font, fill=s.color['black'])
        draw.text((54, i), c, font=font, fill=s.color['white'])

        i += 10

# Print Elsewhere

def elsewhere(draw, data):

    i = 80

    for d in data:
        d = d.split('/')
        if d[0] == '0':
            color = s.color['dimgray']
        else:
            color = s.color['white']

        tmp = d[2].split(':')
        if len(tmp) == 2:
            tmp = '00:' + tmp[0] + ':' + tmp[1]
            d[2] = tmp

        draw.text((1, i), d[1], font=font, fill=s.color['white'])
        draw.text((30, i), d[2], font=font, fill=color)
        draw.text((104, i), d[3], font=font, fill=color)

        i += 10


# Print display on 128 x 32
def display_32():
    with canvas(s.device) as draw:

        # Histogram extended
        if s.transmit is False and s.minute % 2 == 0 and s.seconde < 30:
            draw.rectangle((0, 0, 127, 31), fill=s.color['black'])
            histogram(draw, legacy, 25)

        # If not extended
        else:
            draw.rectangle((0, 0, 127, s.device.height - 1), fill=s.color['black'])

            # Icon talk
            if s.transmit is True:
                draw.text((2, 10), u'\uf130', font=icon, fill=s.color['white'])
                distance(draw)

            # Icon clock (DIY...)
            if s.message[2][:4] == 'Last':
                legacy.text(draw, (0, 8), chr(0) + chr(1), fill=s.color['white'], font=s.SMALL_BITMAP_CLOCK)
                legacy.text(draw, (0, 16), chr(2) + chr(3), fill=s.color['white'], font=s.SMALL_BITMAP_CLOCK)

            # Print data
            i = 0

            for m in s.message:
                if m is not None:
                    w, h = draw.textsize(text=m, font=font)
                    tab = (s.device.width - w) / 2
                    vide = ' ' * 22     # Hack to speed clear screen line...
                    draw.text((0, i), vide, font=font, fill=s.color['white'])
                    draw.text((tab, i), m, font=font, fill=s.color['white'])
                    i += h
                    if i == 24:
                        break

        # Finaly, print clock and room
        clock_room(draw)


# Print display on 128 x 64
def display_64():
    with canvas(s.device) as draw:

        # System log extended Page 1
        if s.transmit is False and s.minute % 2 == 0 and s.seconde < 10:
            extended_system(draw, 1)

        # System log extended Page 2
        elif s.transmit is False and s.minute % 2 == 0 and s.seconde < 20:
            extended_system(draw, 2)

        # Call log extended
        elif s.transmit is False and len(s.call) >=5 and s.minute % 2 == 0 and s.seconde < 30:
            extended_call(draw, len(s.call))

        # Best log extended
        elif s.transmit is False and len(s.best) >= 5 and s.minute % 2 == 0 and s.seconde < 40:
            extended_best(draw, len(s.best))

        # If not extended
        else:
            draw.rectangle((0, 0, 127, s.device.height - 1), fill=s.color['black'])

            for i in xrange(0, 128, 2):
                draw.point((i, 25), fill=s.color['white'])
                draw.point((i, 40), fill=s.color['white'])

            # Icon stat
            draw.text((0, 26), u'\ue801', font=icon, fill=s.color['white'])

            # Icon talk
            if s.transmit is True:
                draw.text((2, 10), u'\uf130', font=icon, fill=s.color['white'])
                distance(draw)

            # Icon clock (DIY...)
            if s.message[2][:4] == 'Last':
                legacy.text(draw, (0, 8), chr(0) + chr(1), fill=s.color['white'], font=s.SMALL_BITMAP_CLOCK)
                legacy.text(draw, (0, 16), chr(2) + chr(3), fill=s.color['white'], font=s.SMALL_BITMAP_CLOCK)

            # Print data
            i = 0

            for m in s.message:
                if m is not None:
                    w, h = draw.textsize(text=m, font=font)
                    tab = (s.device.width - w) / 2
                    vide = ' ' * 22     # Hack to speed clear screen line...
                    draw.text((0, i), vide, font=font, fill=s.color['white'])
                    draw.text((tab, i), m, font=font, fill=s.color['white'])
                    i += h
                    if i == 24:
                        i += 6

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
    with canvas(s.device) as draw:
        draw.rectangle((0, 0, 127, s.device.height - 1), fill=s.color['black'])

        draw.rectangle((0, 0, 128, 14), fill=s.color['darkslategray'])
        draw.rectangle((0, 78, 22, 128), fill=s.color['darkslategray'])

        for i in xrange(0, 128, 1):
            draw.point((i, 0), fill=s.color['dimgray'])
            draw.point((i, 14), fill=s.color['dimgray'])

        # System log extended Page 1
        if s.transmit is False and s.minute % 2 == 0 and s.seconde < 20:
            extended_system(draw, 3)

        # Call log extended
        elif s.transmit is False and len(s.call) >=5 and s.minute % 2 == 0 and s.seconde < 30:
            extended_call(draw, len(s.call))

        # Best log extended
        elif s.transmit is False and len(s.best) >= 5 and s.minute % 2 == 0 and s.seconde < 40:
            extended_best(draw, len(s.best))

        # If not extended
        else:
            for i in xrange(0, 128, 2):
                draw.point((i, 14), fill=s.color['dimgray'])
                draw.point((i, 40), fill=s.color['dimgray'])
                draw.point((i, 78), fill=s.color['dimgray'])
                draw.point((i, 88), fill=s.color['dimgray'])
                draw.point((i, 98), fill=s.color['dimgray'])
                draw.point((i, 108), fill=s.color['dimgray'])
                draw.point((i, 118), fill=s.color['dimgray'])
                
            for i in xrange(78, 128, 2):
                draw.point((22, i), fill=s.color['dimgray'])
                draw.point((98, i), fill=s.color['dimgray'])

            # Icon stat
            draw.text((0, 0), u'\ue801', font=icon, fill=s.color['white'])

            # Icon talk
            if s.transmit is True:
                draw.text((2, 20), u'\uf130', font=icon, fill=s.color['white'])
                distance(draw)

            # Icon clock (DIY...)
            if s.message[2][:4] == 'Last':
                legacy.text(draw, (0, 8), chr(0) + chr(1), fill=s.color['white'], font=s.SMALL_BITMAP_CLOCK)
                legacy.text(draw, (0, 16), chr(2) + chr(3), fill=s.color['white'], font=s.SMALL_BITMAP_CLOCK)

            # Print data
            i = 16
            j = 0
            for m in s.message:
                if m is not None:
                    w, h = draw.textsize(text=m, font=font)
                    tab = (s.device.width - w) / 2
                    vide = ' ' * 22     # Hack to speed clear screen line...
                    if s.transmit is True:
                        if j == 0:
                            color = s.color['white']
                        elif j == 1:
                            color = s.color['gray']
                        else:
                            color = s.color['gray']
                    else:
                        if j == 0:
                            color = s.color['silver']
                        elif j == 1:
                            color = s.color['dimgray']
                        else:
                            color = s.color['dimgray']

                    draw.text((0, i), vide, font=font, fill=s.color['white'])
                    draw.text((tab, i), m, font=font, fill=color)
                    if j < 4:
                        draw.text((16, i), str(j + 1), font=font, fill=color)

                    i += h
                    if i == 40:
                        i = 4
                    j += 1

            if s.transmit is True and s.duration > 0:
                # Draw tot
                tot(draw, legacy, s.duration, 70)
                # Elsewhere
                elsewhere(draw, s.raptor)
            else:
                # Draw stats histogram
                histogram(draw, legacy, 70, 28)
                # Elsewhere
                elsewhere(draw, s.raptor)

        # Finaly, print clock and room
        clock_room(draw)