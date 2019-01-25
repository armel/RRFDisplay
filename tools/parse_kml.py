import re
from math import cos, asin, sqrt

F4HWN_lat = 48.8483808
F4HWN_lon = 2.2704347

# WGS84

def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295        # Pi/180
    a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return round(12742 * asin(sqrt(a)), 1)

data = [line.strip() for line in open('rrf.kml')]

start = False
position = 0
limit = len(data)

while(position < limit):
    line = data[position]
    if start is False:
        if '<Folder>' in line:
            start = True
        position += 1
    elif start is True:
        if '<name>' in line:
            match= re.findall(r'\w+', line)
            print match[2],
            position += 1
        elif '<coordinates>' in line:
            position += 1
            tmp = data[position].split(',')
            print tmp[1], tmp[0]
            # print distance(F4HWN_lat, F4HWN_lon, float(tmp[1]), float(tmp[0]))
            position += 1
        else:
            position += 1
