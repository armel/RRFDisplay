import sys
import os

# Read arg
filename = sys.argv[1]

# Read log file
log = [line.strip() for line in open(filename)]
filename = '/var/www/log/' + os.path.basename(filename) + '/'

if not os.path.exists(filename):
    os.makedirs(filename)
    os.popen('cp /opt/RRFTracker_Spotnik/tools/index.html ' + filename + 'index.html')

# Activity histogram
data = '[\n'

hour_max_when = ''
hour_max_tx = 0

hour_min_when = ''
hour_min_tx = 1000

qso_total = 0

l = 1
for i in xrange(0, 24):
    x, y = log[i].split(' ')

    qso_total += int(y)

    x = str('{:0>2d}'.format(int(x)))
    l = str('{:0>2d}'.format(int(l)))

    if l == '24':
        l = '00'

    x += 'h - ' + l + 'h'

    l = int(l) + 1

    data += '{\n'
    data += '\t"Hour": "' + x + '",\n'
    data += '\t"TX": ' + y + '\n'
    data += '},\n'

    if hour_max_tx < int(y):
        hour_max_tx = int(y)
        hour_max_when = x
    if hour_min_tx > int(y):
        hour_min_tx = int(y)
        hour_min_when = x

data += ']\n'

last = data.rfind(',')
data = data[:last] + '' + data[last + 1:]

file = open(filename + 'activity.json', 'w')
file.write(data)
file.close()

# Last link
data = '[\n'

for i in xrange(25, 25 + 5):
    x = log[i]

    data += '{\n'
    data += '\t"Date": "' + x[0:8] + '",\n'
    data += '\t"Call": ' + x[8:] + '\n'
    data += '},\n'

data += ']\n'

last = data.rfind(',')
data = data[:last] + '' + data[last + 1:]

file = open(filename + 'last.json', 'w')
file.write(data)
file.close()

# Best link: top 20
data = '[\n'

l = 1
for i in xrange(31, len(log)):
    x = log[i].split(' ')

    data += '{\n'
    data += '\t"Call": "' + ' '.join(x[1:-1]) + '",\n'
    data += '\t"TX": ' + x[-1] + '\n'
    data += '},\n'

    l += 1
    if l > 20:
        break

data += ']\n'

last = data.rfind(',')
data = data[:last] + '' + data[last + 1:]

file = open(filename + 'best.json', 'w')
file.write(data)
file.close()

# Best link: all
data = '[\n'

l = 1
for i in xrange(31, len(log)):
    x = log[i].split(' ')

    data += '{\n'
    data += '\t"Pos": ' + str(l) + ',\n'
    data += '\t"Call": "' + ' '.join(x[1:-1]) + '",\n'
    data += '\t"TX": ' + x[-1] + '\n'
    data += '},\n'

    l += 1

data += ']\n'

call_total = l - 1

last = data.rfind(',')
data = data[:last] + '' + data[last + 1:]

file = open(filename + 'all.json', 'w')
file.write(data)
file.close()

# Activity abstract
data = '[\n'

data += '{\n'
data += '\t"TX total": ' + str(qso_total) + ',\n'
data += '\t"Noeuds actifs": ' + str(call_total) + '\n'
data += '},\n'

data += ']\n'

last = data.rfind(',')
data = data[:last] + '' + data[last + 1:]

file = open(filename + 'abstract.json', 'w')
file.write(data)
file.close()
