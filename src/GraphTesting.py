import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import pandas as pd


# reference code: https://matplotlib.org/stable/gallery/lines_bars_and_markers/multicolored_line.html

def get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


csvfile = 'CSVFiles/Tardigrade7hrTrack.csv'
df = pd.read_csv(csvfile)
data = np.genfromtxt(csvfile, delimiter=',', names=['x', 'y'])
x = data['x']
y = data['y']

timev = []
timevadj = []
mint = get_sec(df.min()[2])
maxt = get_sec(df.max()[2])
timediff = maxt - mint

# converts the times to value between 0 and 255 so can do rgb
for index, row in df.iterrows():
    timev.append((get_sec(row['time'])) - mint)

for index, row in df.iterrows():
    timevadj.append(round((255 / timediff) * ((get_sec(row['time'])) - mint), 2))

dydx = np.cos(0.5 * (x[:-1] + x[1:]))  # first derivative

# Create a set of line segments so that we can color them individually
points = np.array([x, y]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111)

# Create a continuous norm to map from data points to colors
norm = plt.Normalize(timev[0], timev[-1])
lc = LineCollection(segments, cmap='copper', norm=norm)
# Set the values used for colormapping
lc.set_array(timevadj)
lc.set_linewidth(2)
line = ax.add_collection(lc)
fig.colorbar(line, ax=ax)

ax.set_xlim(df.min()[0] - 500, df.max()[0] + 500)
ax.set_ylim(df.min()[1] - 500, df.max()[1] + 500)

plt.show()
