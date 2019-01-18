#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
RRFTracker version Raspberry Pi 3B et Orange Pi Zero
Learn more about RRF on https://f5nlg.wordpress.com
Check video about RRFTracker on https://www.youtube.com/watch?v=rVW8xczVpEo
73 & 88 de F4HWN Armel
'''    

# Default i2c_port and i2c_address

i2c_port = 0                            # Default value ! Check port with i2cdetect...
i2c_address = 0x3C                      # Default value ! Check address with i2cdetect...
display = 'sh1106'                      # Default value !
display_width = 128                     # Default value !
display_height = 64                     # Default value !
room = 'RRF'                            # Default value !

# Set constants & variables

SMALL_BITMAP_FONT = [
    [0x1f, 0x11, 0x1f, 0x00],           # 0
    [0x00, 0x1f, 0x00, 0x00],           # 1
    [0x1d, 0x15, 0x17, 0x00],           # 2
    [0x11, 0x15, 0x1f, 0x00],           # 3
    [0x07, 0x08, 0x1c, 0x00],           # 4
    [0x17, 0x15, 0x1d, 0x00],           # 5
    [0x1f, 0x15, 0x1d, 0x00],           # 6
    [0x11, 0x09, 0x07, 0x00],           # 7
    [0x1f, 0x15, 0x1f, 0x00],           # 8
    [0x17, 0x15, 0x1f, 0x00],           # 9
    [0x00, 0x1b, 0x00, 0x00],           # :
    [0x1f, 0x05, 0x1a, 0x00],           # R
    [0x1f, 0x05, 0x01, 0x00],           # F
    [0x1f, 0x11, 0x1f, 0x00],           # O
    [0x01, 0x1f, 0x01, 0x00],           # T
    [0x1f, 0x02, 0x04, 0x1f],           # N
    [0x1f, 0x11, 0x11, 0x00],           # C
    [0x1f, 0x15, 0x11, 0x00]            # E
]

# Set some letters for room

letter = {'C': 16, 'E': 17, 'F': 12, 'N': 15, 'O': 13, 'R': 11, 'T': 14}

# Set call

call = ['F4HWN', 'RRFTracker', '', '', '']	# Call list
call_current = call[0]						# Call current
call_previous = call[1]						# Call previous
call_time = ['Waiting TX', '', '', '', '']	# Call time list

blanc = True								# Detect blank
blanc_alternate = 0							# Detect alternate

qso = 0										# Number of QSO
qso_total = 0								# QSO total
qso_hour = [0] * 24							# QSO list for histogramm

wake_up = True								# Detect wake up on emission
extended = False							# Detect extended state

history = dict()							# History dict
line = [None] * 7							# Line list

# Set url

if room == 'RRF':
    url = 'http://rrf.f5nlg.ovh'
elif room == 'TEC':
    url = 'http://rrf.f5nlg.ovh:82'
elif room == 'FON':
    url = 'http://fon.f1tzo.com:81/'

# Set date

timestamp_start = ''
hour = ''
minute = ''
seconde = ''