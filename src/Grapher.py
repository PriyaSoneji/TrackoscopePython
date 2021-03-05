import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import cm
import matplotlib.collections as mcoll
import matplotlib.path as mpath
import pandas as pd
import mplcursors

csvfile = 'CSVFiles/Tardigrade7hrTrack.csv'
df = pd.read_csv(csvfile)


def get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


timev = []
mint = get_sec(df.min()[2])
maxt = get_sec(df.max()[2])
timediff = maxt - mint

# converts the times to value between 0 and 255 so can do rgb
for index, row in df.iterrows():
    timev.append(round((255 / timediff) * ((get_sec(row['time'])) - mint), 2))


def colorline(
        x, y, z=None, cmap=plt.get_cmap('copper'), norm=plt.Normalize(0.0, 1.0),
        linewidth=3, alpha=1.0):
    # Default colors equally spaced on [0,1]:
    if z is None:
        z = np.linspace(0.0, 1.0, len(x))

    # Special case if a single number:
    if not hasattr(z, "__iter__"):  # to check for numerical input -- this is a hack
        z = np.array([z])

    z = np.asarray(z)

    segments = make_segments(x, y)
    lc = mcoll.LineCollection(segments, array=z, cmap=cmap, norm=norm,
                              linewidth=linewidth, alpha=alpha)

    ax = plt.gca()
    ax.set_xlim(df.min()[0] - 500, df.max()[0] + 500)
    ax.set_ylim(df.min()[1] - 500, df.max()[1] + 500)
    ax.add_collection(lc)

    return lc


def make_segments(x, y):
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    return segments


data = np.genfromtxt(csvfile, delimiter=',', names=['x', 'y'])
x = data['x']
y = data['y']
# tv = np.cos(x)

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111)

for i in range(10):
    colorline(x, y, cmap='cubehelix', linewidth=1)

mplcursors.cursor()

plt.show()
