#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
RRFTracker version Raspberry Pi 3B et Orange Pi Zero
Learn more about RRF on https://f5nlg.wordpress.com
Check video about RRFTracker on https://www.youtube.com/watch?v=rVW8xczVpEo
73 & 88 de F4HWN Armel
'''

# Version

version = '3.0.4'

# Default i2c_port, i2c_address, display and room

i2c_port = 0                            # Default value ! Check with i2detect
i2c_address = 0x3C                      # Default value ! Check with i2detect
display = 'sh1106'                      # Default value !
display_width = 128                     # Default value !
display_height = 64                     # Default value !
room_current = 'RRF'                    # Default value !
callsign = 'F4HWN'                      # Default value !
scan = False                            # Default value !
latitude = 48.8483808                   # Default value ! Check WGS84 on https://www.coordonnees-gps.fr/
longitude = 2.2704347                   # Default value ! Check WGS84 on https://www.coordonnees-gps.fr/

# Set special small bitmap font for clock and cpu

SMALL_BITMAP_CLOCK = [
    [0x00, 0xc0, 0x20, 0x10, 0x14, 0x0c, 0xec, 0x0c],
    [0x14, 0x10, 0x20, 0xc0, 0x00, 0x00, 0x00, 0x00],
    [0x07, 0x18, 0x20, 0x40, 0x40, 0x80, 0x83, 0x82],
    [0x42, 0x40, 0x20, 0x18, 0x07, 0x00, 0x00, 0x00]
]

'''
SMALL_BITMAP_CPU = [
    [0xf0, 0x1c, 0x90, 0x90, 0x9c, 0x10, 0x90, 0x9c],
    [0x90, 0x10, 0x9c, 0x10, 0x90, 0x1c, 0xf0, 0x00],
    [0x3f, 0xe0, 0x27, 0x24, 0xe4, 0x20, 0x27, 0xe2],
    [0x23, 0x20, 0xe7, 0x24, 0x27, 0xe0, 0x3f, 0x00]
]
'''

SMALL_BITMAP_CPU = [
    [0xff, 0xff, 0x80, 0x01, 0x80, 0x01, 0x80, 0x01],
    [0x80, 0x01, 0x80, 0x01, 0x80, 0x01, 0x80, 0x01], 
    [0x80, 0x01, 0x80, 0x01, 0x80, 0x01, 0x80, 0x01], 
    [0x80, 0x01, 0x80, 0x01, 0x80, 0x01, 0xff, 0xff]
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
    [0x1f, 0x10, 0x10, 0x00],           # L
    [0x11, 0x1f, 0x11, 0x00],           # I
    [0x1e, 0x05, 0x1e, 0x00],           # A
    [0x1f, 0x15, 0x0a, 0x00],           # B
    [0x0f, 0x18, 0x0f, 0x00],           # V
    [0x1f, 0x06, 0x0c, 0x06, 0x1f],     # M
    [0x00, 0x00, 0x00, 0x00]            # Space
]

# Room list

room = {
    'RRF': {
        'url': 'http://rrf.f5nlg.ovh:8080/RRFTracker/RRF-today/rrf_tiny.json',
        'api': 'http://rrf.f5nlg.ovh/api/svxlink/RRF'
    }, 
    'TECHNIQUE': {
        'url': 'http://rrf.f5nlg.ovh:8080/RRFTracker/TECHNIQUE-today/rrf_tiny.json',
        'api': 'http://rrf.f5nlg.ovh/api/svxlink/technique'
    }, 
    'INTERNATIONAL': {
        'url': 'http://rrf.f5nlg.ovh:8080/RRFTracker/INTERNATIONAL-today/rrf_tiny.json',
        'api': 'http://rrf.f5nlg.ovh/api/svxlink/international'
    }, 
    'LOCAL': {
        'url': 'http://rrf.f5nlg.ovh:8080/RRFTracker/LOCAL-today/rrf_tiny.json',
        'api': 'http://rrf.f5nlg.ovh/api/svxlink/local'
    },  
    'BAVARDAGE': {
        'url': 'http://rrf.f5nlg.ovh:8080/RRFTracker/BAVARDAGE-today/rrf_tiny.json',
        'api': 'http://rrf.f5nlg.ovh/api/svxlink/bavardage'
    },  
    'FON': {
        'url': 'http://rrf.f5nlg.ovh:8080/RRFTracker/FON-today/rrf_tiny.json',
        'api': 'http://rrf.f5nlg.ovh/api/svxlink/FON'
    }
}

# Set some letters for room

letter = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
    '8': 8, '9': 9, ':': 10, '.': 11, 'R': 12, 'F': 13, 'O': 14,
    'T': 15, 'N': 16, 'C': 17, 'E': 18, 'K': 19, 'L': 20, 'I': 21, 'A': 22, 'B': 23, 'V': 24, 'M': 25, ' ': 26
}

# Set variables

call = [''] * 10            # Call list
call_time = [''] * 10       # Call time list
best = [''] * 10            # Best list
best_time = [0] * 10        # Best time list
call_current = call[0]      # Call current
qso_hour = [0] * 24         # QSO list for histogramm
transmit = True             # Detect transmit
transmit_elsewhere = True   # Detect transmit elsewhere
history = dict()            # History dict
message = [None] * 10       # Message list
raptor = [None] * 5         # Message list

# Set color

color = {
    'black': int('0x000000', 16),
    'darkslategray': int('0x111111', 16),
    'dimgray': int('0x222222', 16),
    'gray': int('0x333333', 16),
    'silver': int('0x4444444', 16),
    'white': int('0xffffff', 16)
}

# Set time and date

timestamp_start = ''
hour = ''
minute = ''
seconde = ''