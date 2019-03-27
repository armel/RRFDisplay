import sys
import os
import plotly
import plotly.graph_objs as go
from plotly import tools

# Read arg
filename = sys.argv[1]

# Read log file
log = [line.strip() for line in open(filename)]

# Activity histogram
t = []
q = []
l = 1
for i in xrange(2, 2 + 24):
    x, y = log[i].split(' ')

    x = str('{:0>2d}'.format(int(x)))
    l = str('{:0>2d}'.format(int(l)))

    if l == '24':
        l = '00'

    x += 'h - ' + l + 'h'

    l = int(l) + 1
    t.append(x)
    q.append(y)

# Best link
c = []
n = []
l = 0
for i in xrange(27, len(log)):
    x = log[i].split(' ')
    c.append(' '.join(x[1:-1]))
    n.append(x[-1])
    l += 1

# Trace
trace_history = go.Histogram(
    histfunc='sum',
    y=q,
    x=t,
    opacity=0.75
)

trace_best = go.Bar(
    x=n,
    y=c,
    orientation='h',
    opacity=0.75
)

layout = dict(
    title='Salon ' + filename[4:7] + ' ' + filename[8:]
)

print os.path.basename(filename)

exit(0)

# Creating two subplots
fig = tools.make_subplots(rows=1,
                          cols=2,
                          specs=[[{}, {}]],
                          shared_xaxes=True,
                          shared_yaxes=False,
                          subplot_titles=('24 hours Activity / ' + str(log[0]) + ' QSOs', 'Nodes Activity / ' + str(l) + ' active nodes'),
                          vertical_spacing=0.001)

fig['layout'].update(layout)

fig.append_trace(trace_history, 1, 1)
fig.append_trace(trace_best, 1, 2)

fig['layout'].update(layout)
plotly.offline.plot(fig, filename='html/' + filename[4:] + '.html')
