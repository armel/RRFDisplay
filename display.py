#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
RRFTracker version Raspberry Pi 3B et Orange Pi Zero
Learn more about RRF on https://f5nlg.wordpress.com
Check video about RRFTracker on https://www.youtube.com/watch?v=rVW8xczVpEo
73 & 88 de F4HWN Armel
'''

import config

def display_32():
	return

def display_64():
    if config.extended is False:

        if 'Waiting TX' not in config.call_time and len(config.history) >= 5 and config.device.height == 64:
            config.extended = True

    if config.wake_up is False and config.minute % 2 == 0 and config.seconde < 20:                               # System log extended

        draw.rectangle((0, 0, 127, 63), fill='black')

        draw.text((0, 0), u'\ue801', font=icon, fill='white')

        w, h = draw.textsize(text='Spotnik Infos', font=font)
        tab = (device.width - w) / 2
        draw.text((tab, 0), 'Spotnik Infos', font=font, fill='white')

        sys = {'Load': '', 'Temp': '', 'Freq': '', 'Mem': '', 'Disk': ''}

        a, b, c = system_info('load')
        sys['Load'] = a + ' ' + b + ' ' + c

        sys['Temp'] = system_info('temp') + ' C'

        sys['Freq'] = system_info('freq') + ' MHz'

        percent, mem = system_info('mem')
        sys['Mem'] = percent + '% of ' + mem

        percent, disk = system_info('disk')
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

    elif config.wake_up is False and config.extended is True and config.minute % 2 == 0 and config.seconde < 40:        # History log extended

        draw.rectangle((0, 0, 127, 63), fill='black')

        x = 6
        y = 6
        draw.ellipse((x - 6, y - 6, x + 6, y + 6), outline='white')
        draw.line((x, y, x + 2, y + 2), fill='white')
        draw.line((x, y, x, y - 3), fill='white')

        w, h = draw.textsize(text=config.room + ' Last TX', font=font)
        tab = (config.device.width - w) / 2
        draw.text((tab, 0), config.room + ' Last TX', font=font, fill='white')

        i = 16

        for j in xrange(0, 5):
            draw.rectangle((0, i - 1, 42, i + 7), fill='white')
            draw.line((43, i, 43, i + 6), fill='white')
            draw.line((44, i + 2, 44, i + 4), fill='white')
            draw.point((45, i + 3), fill='white')

            draw.text((1, i), config.call_time[j], font=font, fill='black')
            draw.text((54, i), config.call[j], font=font, fill='white')

            i += 10

    elif config.wake_up is False and config.extended is True and config.minute % 2 == 0:                         # Best log extended

        draw.rectangle((0, 0, 127, 63), fill='black')

        draw.text((0, 0), u'\ue801', font=icon, fill='white')

        w, h = draw.textsize(text=config.room + ' Best TX', font=font)
        tab = (device.width - w) / 2
        draw.text((tab, 0), room + ' Best TX', font=font, fill='white')

        tmp = sorted(history.items(), key=lambda x: x[1])
        tmp.reverse()

        best_min = min(config.history, key=config.history.get)
        best_max = max(config.history, key=config.history.get)

        i = 16

        for j in xrange(0, 5):
            c, n = tmp[j]
            t = interpolation(n, history[best_min], history[best_max], 12, 42)
            n = str(n)

            draw.rectangle((0, i - 1, t, i + 7), fill='white')
            draw.line((t + 1, i, t + 1, i + 6), fill='white')
            draw.line((t + 2, i + 2, t + 2, i + 4), fill='white')
            draw.point((t + 3, i + 3), fill='white')

            draw.text((1, i), n, font=font, fill='black')
            draw.text((54, i), c, font=font, fill='white')

            i += 10

    else:                                                               # If not extended

        if config.device.height == 64:     # Only if 128 x 64 pixels
            for i in xrange(0, 128, 2):
                draw.point((i, 25), fill='white')
                draw.point((i, 40), fill='white')
                draw.text((0, 26), u'\ue801', font=icon, fill='white')  # Icon stat

        if config.wake_up is True:
            draw.text((2, 0), u'\uf130', font=icon, fill='white')       # Icon talk

        if line[2][:4] == 'Last':                                       # Icon clock (DIY...)
            x = 6
            y = 17
            draw.ellipse((x - 6, y - 6, x + 6, y + 6), outline='white')
            draw.line((x, y, x + 2, y + 2), fill='white')
            draw.line((x, y, x, y - 3), fill='white')

        # Print data

        i = 0

        for l in line:
            if l is not None:
                w, h = draw.textsize(text=l, font=font)
                tab = (config.device.width - w) / 2
                vide = ' ' * 22             # Hack to speed clear screen line...
                draw.text((0, i), vide, font=font, fill='white')
                draw.text((tab, i), l, font=font, fill='white')
                i += h
                if i == 24:
                    if config.device.height != 64:  # Break if 128 x 32 pixels
                        break
                    i += 6

        # Draw stats histogram

        if config.device.height == 64:              # Only if 128 x 64 pixels

            qso_hour_max = max(qso_hour)

            i = 4

            for q in config.qso_hour:
                if q != 0:
                    h = interpolation(q, 1, qso_hour_max, 1, 15)
                else:
                    h = 0
                draw.rectangle((0 + i, 57, i + 2, (57 - 15)), fill='black')
                draw.rectangle((0 + i, 57, i + 2, (57 - h)), fill='white')
                i += 5

            legacy.text(draw,   (4, 59), chr(0) + chr(0), fill='white', font=SMALL_BITMAP_FONT)
            legacy.text(draw,  (32, 59), chr(0) + chr(6), fill='white', font=SMALL_BITMAP_FONT)
            legacy.text(draw,  (62, 59), chr(1) + chr(2), fill='white', font=SMALL_BITMAP_FONT)
            legacy.text(draw,  (92, 59), chr(1) + chr(8), fill='white', font=SMALL_BITMAP_FONT)
            legacy.text(draw, (115, 59), chr(2) + chr(3), fill='white', font=SMALL_BITMAP_FONT)

    if config.blanc_alternate == 3:
        # Print Room

        i = 115

        for c in config.room:
            legacy.text(draw,  (i, 1), chr(letter[c]), fill='white', font=SMALL_BITMAP_FONT)
            i += 4
    else:
        # Print Clock

        i = 108

        for c in now:
            if c == ':':
                c = 10
            else:
                c = int(c)
            legacy.text(draw,  (i, 1), chr(c), fill='white', font=SMALL_BITMAP_FONT)
            i += 4