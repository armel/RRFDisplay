import sys
import os
import plotly

# Read arg
filename = sys.argv[1]

# Read log file
log = [line.strip() for line in open(filename)]
filename = os.path.basename(filename)

# Activity histogram
data = '[\n'

l = 1
for i in xrange(2, 2 + 24):
    x, y = log[i].split(' ')

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

data += ']\n'

last = data.rfind(',')
data = data[:last] + '' + data[last + 1:]

file = open(filename + '-activity.json', 'w')
file.write(data)
file.close()


# Best link
data = '[\n'

l = 1
for i in xrange(27, len(log)):
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

file = open(filename + '-best.json', 'w')
file.write(data)
file.close()

# Best link
filename = '/var/www/log/all.json'

data = '[\n'

l = 1
for i in xrange(27, len(log)):
    x = log[i].split(' ')

    data += '{\n'
    data += '\t"Pos": ' + str(l) + ',\n'
    data += '\t"Call": "' + ' '.join(x[1:-1]) + '",\n'
    data += '\t"TX": ' + x[-1] + '\n'
    data += '},\n'

    l += 1

data += ']\n'

last = data.rfind(',')
data = data[:last] + '' + data[last + 1:]

file = open(filename + '-all.json', 'w')
file.write(data)
file.close()
