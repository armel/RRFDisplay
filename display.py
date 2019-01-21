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

font = ImageFont.truetype('fonts/7x5.ttf', 8)           # Text font
icon = ImageFont.truetype('fonts/fontello.ttf', 14)     # Icon font


# Draw tot
def tot(draw, legacy, start, current, position):
    duration = int(current) - int(start)
    duration_min = 0

    timer = [i for i in xrange(30, 901, 30)]

    for i in timer:
        if duration < i:
            duration_max = i
            break
        else:
            duration_min = i

    h = l.interpolation(duration, duration_min, duration_max, 0, 120)

    draw.rectangle((0, 54, 128, 43), fill='black')
    for i in xrange(3, h, 2):
        draw.rectangle((i, 54, i, 43), fill='white')

    for i in xrange(3, 124, 4):
        print i
        draw.line((i, 57, i + 1, 57), fill='white')

    draw.line((63, 0, 63, 63), fill='white')

    # Duration min
    tmp = list(str(duration_min))
    msg = ''
    for c in tmp:
        msg += chr(int(c))
    legacy.text(draw, (0, position + 2), msg, fill='white', font=s.SMALL_BITMAP_FONT)
    
    # Duration max
    tmp = list(str(duration_max))
    msg = ''
    for c in tmp:
        msg += chr(int(c))
    if duration_max < 100:
        tab = 4
    else:
        tab = 0
    legacy.text(draw, (115 + tab, position + 2), msg, fill='white', font=s.SMALL_BITMAP_FONT)

    # duration
    tmp = list(str(duration))
    msg = ''
    for c in tmp:
        msg += chr(int(c))
    if duration_max < 10:
        tab = 4
    else:
        tab = 0
    legacy.text(draw, (60 + tab, position + 2), msg, fill='white', font=s.SMALL_BITMAP_FONT)

# Draw histogram
def histogram(draw, legacy, position):

    qso_hour_max = max(s.qso_hour)

    i = 5

    for q in s.qso_hour:
        if q != 0:
            h = l.interpolation(q, 1, qso_hour_max, 1, 15)
        else:
            h = 0

        #print i
        draw.rectangle((0 + i, position, i + 2, (position - 15)), fill='black')
        draw.rectangle((0 + i, position, i + 2, (position - h)), fill='white')
        i += 5

    legacy.text(draw,   (1, position + 2), chr(0) + chr(0), fill='white', font=s.SMALL_BITMAP_FONT)
    legacy.text(draw,  (33, position + 2), chr(0) + chr(6), fill='white', font=s.SMALL_BITMAP_FONT)
    legacy.text(draw,  (63, position + 2), chr(1) + chr(2), fill='white', font=s.SMALL_BITMAP_FONT)
    legacy.text(draw,  (93, position + 2), chr(1) + chr(8), fill='white', font=s.SMALL_BITMAP_FONT)
    legacy.text(draw, (120, position + 2), chr(2) + chr(3), fill='white', font=s.SMALL_BITMAP_FONT)


# Print clock and room
def clock_room(draw):

    # Print Room
    if s.blanc_alternate == 3:
        i = 115

        for c in s.room:
            legacy.text(draw,  (i, 1), chr(s.letter[c]), fill='white', font=s.SMALL_BITMAP_FONT)
            i += 4

    # Print Clock
    else:
        i = 108

        for c in s.now:
            if c == ':':
                c = 10
            else:
                c = int(c)
            legacy.text(draw,  (i, 1), chr(c), fill='white', font=s.SMALL_BITMAP_FONT)
            i += 4


# print System Log Extended

def extended_system(draw):

    draw.rectangle((0, 0, 127, 63), fill='black')

    draw.text((0, 0), u'\ue801', font=icon, fill='white')

    w, h = draw.textsize(text='Spotnik Infos', font=font)
    tab = (s.device.width - w) / 2
    draw.text((tab, 0), 'Spotnik Infos', font=font, fill='white')

    sys = {'Load': '', 'Temp': '', 'Freq': '', 'Mem': '', 'Disk': ''}

    a, b, c = l.system_info('load')
    sys['Load'] = a + ' ' + b + ' ' + c

    sys['Temp'] = l.system_info('temp') + ' C'

    sys['Freq'] = l.system_info('freq') + ' MHz'

    percent, mem = l.system_info('mem')
    sys['Mem'] = percent + '% of ' + mem

    percent, disk = l.system_info('disk')
    sys['Disk'] = percent + '% of ' + disk

    i = 16

    for j in ['Load', 'Temp', 'Freq', 'Mem', 'Disk']:
        draw.rectangle((0, i - 1, 30, i + 7), fill='white')
        draw.line((31, i, 31, i + 6), fill='white')
        draw.line((32, i + 2, 32, i + 4), fill='white')
        draw.point((33, i + 3), fill='white')

        draw.text((1, i), j, font=font, fill='black')
        draw.text((42, i), sys[j], font=font, fill='white')

        i += 10


# print History Log Extended

def extended_history(draw):

    draw.rectangle((0, 0, 127, 63), fill='black')

    x = 6
    y = 6
    draw.ellipse((x - 6, y - 6, x + 6, y + 6), outline='white')
    draw.line((x, y, x + 2, y + 2), fill='white')
    draw.line((x, y, x, y - 3), fill='white')

    w, h = draw.textsize(text=s.room + ' Last TX', font=font)
    tab = (s.device.width - w) / 2
    draw.text((tab, 0), s.room + ' Last TX', font=font, fill='white')

    i = 16

    for j in xrange(0, 5):
        draw.rectangle((0, i - 1, 42, i + 7), fill='white')
        draw.line((43, i, 43, i + 6), fill='white')
        draw.line((44, i + 2, 44, i + 4), fill='white')
        draw.point((45, i + 3), fill='white')

        draw.text((1, i), s.call_time[j], font=font, fill='black')
        draw.text((54, i), s.call[j], font=font, fill='white')

        i += 10


# print Best Log Extended

def extended_best(draw):

    draw.rectangle((0, 0, 127, 63), fill='black')

    draw.text((0, 0), u'\ue801', font=icon, fill='white')

    w, h = draw.textsize(text=s.room + ' Best TX', font=font)
    tab = (s.device.width - w) / 2
    draw.text((tab, 0), s.room + ' Best TX', font=font, fill='white')

    tmp = sorted(s.history.items(), key=lambda x: x[1])
    tmp.reverse()

    best_min = min(s.history, key=s.history.get)
    best_max = max(s.history, key=s.history.get)

    i = 16

    for j in xrange(0, 5):
        c, n = tmp[j]
        t = l.interpolation(n, s.history[best_min], s.history[best_max], 12, 42)
        n = str(n)

        draw.rectangle((0, i - 1, t, i + 7), fill='white')
        draw.line((t + 1, i, t + 1, i + 6), fill='white')
        draw.line((t + 2, i + 2, t + 2, i + 4), fill='white')
        draw.point((t + 3, i + 3), fill='white')

        draw.text((1, i), n, font=font, fill='black')
        draw.text((54, i), c, font=font, fill='white')

        i += 10


# Print display on 128 x 32
def display_32():
    with canvas(s.device) as draw:

        # Check if extended
        if s.extended is False:
            if 'Waiting TX' not in s.call_time and len(s.history) >= 5:
                s.extended = True

        # Histogram extended
        if s.wake_up is False and s.minute % 2 == 0 and s.seconde < 30:
            draw.rectangle((0, 0, 127, 31), fill='black')
            histogram(draw, legacy, 25)

        # If not extended
        else:
            draw.rectangle((0, 0, 127, 31), fill='black')

            # Icon talk
            if s.wake_up is True:
                draw.text((2, 0), u'\uf130', font=icon, fill='white')

            # Icon clock (DIY...)
            if s.message[2][:4] == 'Last':
                x = 6
                y = 17
                draw.ellipse((x - 6, y - 6, x + 6, y + 6), outline='white')
                draw.line((x, y, x + 2, y + 2), fill='white')
                draw.line((x, y, x, y - 3), fill='white')

            # Print data
            i = 0

            for m in s.message:
                if m is not None:
                    w, h = draw.textsize(text=m, font=font)
                    tab = (s.device.width - w) / 2
                    vide = ' ' * 22     # Hack to speed clear screen line...
                    draw.text((0, i), vide, font=font, fill='white')
                    draw.text((tab, i), m, font=font, fill='white')
                    i += h
                    if i == 24:
                        break

        # Finaly, print clock and room
        clock_room(draw)


# Print display on 128 x 64
def display_64():
    with canvas(s.device) as draw:

        # Check if extended
        if s.extended is False:
            if 'Waiting TX' not in s.call_time and len(s.history) >= 5:
                s.extended = True

        # System log extended
        if s.wake_up is False and s.minute % 2 == 0 and s.seconde < 20:
            extended_system(draw)
            
        # History log extended
        elif s.wake_up is False and s.extended is True and s.minute % 2 == 0 and s.seconde < 40:
            extended_history(draw)
            
        # Best log extended
        elif s.wake_up is False and s.extended is True and s.minute % 2 == 0:
            extended_best(draw)

        # If not extended
        else:

            for i in xrange(0, 128, 2):
                draw.point((i, 25), fill='white')
                draw.point((i, 40), fill='white')

            # Icon stat
            draw.text((0, 26), u'\ue801', font=icon, fill='white')

            # Icon talk
            if s.wake_up is True:
                draw.text((2, 0), u'\uf130', font=icon, fill='white')

            # Icon clock (DIY...)
            if s.message[2][:4] == 'Last':
                x = 6
                y = 17
                draw.ellipse((x - 6, y - 6, x + 6, y + 6), outline='white')
                draw.line((x, y, x + 2, y + 2), fill='white')
                draw.line((x, y, x, y - 3), fill='white')

            # Print data
            i = 0

            for m in s.message:
                if m is not None:
                    w, h = draw.textsize(text=m, font=font)
                    tab = (s.device.width - w) / 2
                    vide = ' ' * 22     # Hack to speed clear screen line...
                    draw.text((0, i), vide, font=font, fill='white')
                    draw.text((tab, i), m, font=font, fill='white')
                    i += h
                    if i == 24:
                        i += 6

            if s.wake_up is True and s.tot_current > s.tot_start:
            # Draw tot
                tot(draw, legacy, s.tot_start, s.tot_current, 57)
            else:
                # Draw stats histogram
                histogram(draw, legacy, 57)

        # Finaly, print clock and room
        clock_room(draw)
