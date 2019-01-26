#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
RRFTracker version Raspberry Pi 3B et Orange Pi Zero
Learn more about RRF on https://f5nlg.wordpress.com
Check video about RRFTracker on https://www.youtube.com/watch?v=rVW8xczVpEo
73 & 88 de F4HWN Armel
'''

# Version

version = '2.3.0'

# Default i2c_port, i2c_address, display and room

i2c_port = 0                            # Default value !
i2c_address = 0x3C                      # Default value !
display = 'sh1106'                      # Default value !
display_width = 128                     # Default value !
display_height = 64                     # Default value !
room = 'RRF'                            # Default value !

# My informations

my_call = 'F4HWN'
my_latitude = 48.8483808                # WGS84 https://www.coordonnees-gps.fr/
my_longitude = 2.2704347                # WGS84 https://www.coordonnees-gps.fr/

# Set special small bitmap font for clock and room

SMALL_BITMAP_CLOCK = [
    [0xe0, 0x18, 0x04, 0x04, 0x02, 0x7a, 0x42, 0x44],
    [0x04, 0x18, 0xe0, 0x00, 0x00, 0x00, 0x00, 0x00],
    [0x00, 0x03, 0x04, 0x04, 0x08, 0x08, 0x08, 0x04],
    [0x04, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
]

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
    [0x00, 0x18, 0x00, 0x00],           # .
    [0x1f, 0x05, 0x1a, 0x00],           # R
    [0x1f, 0x05, 0x01, 0x00],           # F
    [0x1f, 0x11, 0x1f, 0x00],           # O
    [0x01, 0x1f, 0x01, 0x00],           # T
    [0x1f, 0x06, 0x0c, 0x1f],           # N
    [0x1f, 0x11, 0x11, 0x00],           # C
    [0x1f, 0x15, 0x11, 0x00],           # E
    [0x1f, 0x04, 0x0a, 0x11],           # K
    [0x1f, 0x06, 0x0c, 0x06, 0x1f],     # M
    [0x00, 0x00, 0x00, 0x00]            # Space
]

# Set some letters for room

letter = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
    '8': 8, '9': 9, ':': 10, '.': 11, 'R': 12, 'F': 13, 'O': 14,
    'T': 15, 'N': 16, 'C': 17, 'E': 18, 'K': 19, 'M': 20, ' ': 21
}

# Set call

call = ['F4HWN', 'RRFTracker', '', '', '']  # Call list
call_current = call[0]                      # Call current
call_previous = call[1]                     # Call previous
call_time = ['Waiting TX', '', '', '', '']  # Call time list

blanc = True                                # Detect blank
blanc_alternate = 0                         # Detect alternate

qso = 0                                     # QSO count
qso_total = 0                               # QSO total count
qso_hour = [0] * 24                         # QSO list for histogramm
wake_up = True                              # Detect wake up on emission
extended = False                            # Detect extended state

history = dict()                            # History dict
message = [None] * 7                        # Message list

# Set time and date

timestamp_start = ''
tot_start = ''
tot_current = ''
hour = ''
minute = ''
seconde = ''
