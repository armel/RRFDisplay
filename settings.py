#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
RRFDisplay version Raspberry Pi 3B et Orange Pi Zero
Learn more about RRF on https://f5nlg.wordpress.com
Check video about RRFDisplay on https://www.youtube.com/watch?v=rVW8xczVpEo
73 & 88 de F4HWN Armel
'''

# Version

version = '5.5.0'

# Default i2c_port, i2c_address, display and room

interface = 'i2c'                       # Default value !
spi_device = 0                          # Default value !
i2c_port = 0                            # Default value ! Check with i2detect
i2c_address = 0x3C                      # Default value ! Check with i2detect
display = 'ssd1327'                     # Default value !
framebuffer_device = '/dev/fb0'         # Default value !
display_width = 128                     # Default value !
display_height = 128                    # Default value !
display_theme = 'gray.cfg'              # Default value ! 
follow = 'RRF'                          # Default value !
refresh = 1.0                           # Default value !
latitude = 48.8482855                   # Default value ! Check WGS84 on https://www.coordonnees-gps.fr/
longitude = 2.2708201                   # Default value ! Check WGS84 on https://www.coordonnees-gps.fr/

# Set special small bitmap font for clock and cpu

SMALL_BITMAP_CPU = [
    [0xfe, 0x03, 0xf2, 0x92, 0x93, 0x02, 0xf2, 0x53],
    [0x72, 0x02, 0xf3, 0x82, 0xf2, 0x03, 0xfe, 0x00],
    [0x07, 0x0c, 0x04, 0x04, 0x0c, 0x04, 0x04, 0x0c], 
    [0x04, 0x04, 0x0c, 0x04, 0x04, 0x0c, 0x07, 0x00]
]

SMALL_BITMAP_STAT = [
    [0xff, 0x00, 0xc0, 0xc0, 0x00, 0xfc, 0xfc, 0x00],
    [0xf0, 0xf0, 0x00, 0xff, 0xff, 0x00, 0x00, 0x00],
    [0x0f, 0x08, 0x0b, 0x0b, 0x08, 0x0b, 0x0b, 0x08],
    [0x0b, 0x0b, 0x08, 0x0b, 0x0b, 0x08, 0x08, 0x00]
]

SMALL_BITMAP_CLOCK = [
    [0xf0, 0x08, 0x04, 0x02, 0x02, 0x7a, 0x42, 0x42],
    [0x04, 0x08, 0xf0, 0x00, 0x00, 0x00, 0x00, 0x00],
    #[0x04, 0x08, 0xf0, 0x40, 0xe0, 0x00, 0x00, 0x00],
    [0x01, 0x02, 0x04, 0x08, 0x08, 0x08, 0x08, 0x08],
    [0x04, 0x02, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00]
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

where = 'http://217.182.206.155:8080/RRFTracker'
#where = 'http://rrf.f5nlg.ovh:8080/RRFTracker'
#where = 'http://192.168.1.101/RRFTracker'

room = {
    'RRF': {
        'url': where + '/RRF-today/rrf_tiny.json',
        'api': 'http://rrf2.f5nlg.ovh:4440/nodes'
    }, 
    'TECHNIQUE': {
        'url':  where + '/TECHNIQUE-today/rrf_tiny.json',
        'api': 'http://rrf2.f5nlg.ovh:4440/nodes'
    }, 
    'INTERNATIONAL': {
        'url': where + '/INTERNATIONAL-today/rrf_tiny.json',
        'api': 'http://rrf2.f5nlg.ovh:4440/nodes'
    }, 
    'LOCAL': {
        'url': where + '/LOCAL-today/rrf_tiny.json',
        'api': 'http://rrf2.f5nlg.ovh:4440/nodes'
    },  
    'BAVARDAGE': {
        'url': where + '/BAVARDAGE-today/rrf_tiny.json',
        'api': 'http://rrf2.f5nlg.ovh:4440/nodes'
    },  
    'FON': {
        'url': where + '/FON-today/rrf_tiny.json',
        'api': 'http://rrf2.f5nlg.ovh:4440/nodes'
    }
}

# Set some letters for room

letter = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
    '8': 8, '9': 9, ':': 10, '.': 11, 'R': 12, 'F': 13, 'O': 14,
    'T': 15, 'N': 16, 'C': 17, 'E': 18, 'K': 19, 'L': 20, 'I': 21, 'A': 22, 'B': 23, 'V': 24, 'M': 25, ' ': 26
}

# Set variables

room_current = 'RRF'        # Current Room
callsign = 'F4HWN'          # Callsign if follow
scan = False                # Scan mode
follow_list = {}            # Follow list
theme_list = {}             # Theme list
offset_list = {1: 0}        # Screen offset

call = [''] * 10            # Call list
call_time = [''] * 10       # Call time list
best = [''] * 10            # Best list
best_time = [0] * 10        # Best time list
iptable = [''] * 5          # Iptable list
iptable_by = [''] * 5       # Iptable by list

call_current = call[0]      # Call current
call_type = ''              # Call type
call_description = ''       # Call description
call_tone = ''              # Call tone
call_locator = ''           # Call locator
call_sysop = ''             # Call sysop
call_latitude = ''          # Call latitude
call_longitude = ''         # Call longitude
call_prenom = ''            # Call prenom
qso_hour = [0] * 24         # QSO list for histogramm
duration = 0                # QSO time
transmit = True             # Detect transmit
transmit_elsewhere = True   # Detect transmit elsewhere
history = dict()            # History dict
message = [''] * 10         # Message list
raptor = [None] * 5         # Message list

# Set special color for SSD1327

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

# Set solar

solar_url = 'http://www.hamqsl.com/solarxml.php'
solar_file = './data/solar.xml'
solar_value = {}

# Set greyline

greyline_url = 'https://dx.qsl.net/propagation/greyline.html'
greyline_image = './data/greyline.jpg'

# Set cluster

cluster_url = 'http://www.dxcluster.co.uk/api/data_band/'
cluster_file = './data/cluster.json'
cluster_band = '10'
cluster_band_file = './data/band.dat'
cluster_value = {}
cluster_exclude = {
    '2': ['144174'],
    '6': ['50313'],
    '10': ['28074', '28080'],
    '12': ['24915'],
    '15': ['21074'],
    '17': ['18100'],
    '20': ['14074'],
    '30': ['10136'],
    '40': ['7074'],
    '60': ['5357'],
    '80': ['3573'],
    '160': ['1840']
}
