import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import pandas as pd


def get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


csvfile = 'CSVFiles/Tardigrade7hrTrack.csv'
df = pd.read_csv(csvfile)
data = np.genfromtxt(csvfile, delimiter=',', names=['x', 'y'])
x = data['x']
y = data['y']

timev = []
mint = get_sec(df.min()[2])
maxt = get_sec(df.max()[2])
timediff = maxt - mint

# converts the times to value between 0 and 255 so can do rgb
for index, row in df.iterrows():
    timev.append(round((255 / timediff) * ((get_sec(row['time'])) - mint), 2))

dydx = np.cos(0.5 * (x[:-1] + x[1:]))  # first derivative

# Create a set of line segments so that we can color them individually
# This creates the points as a N x 1 x 2 array so that we can stack points
# together easily to get the segments. The segments array for line collection
# needs to be (numlines) x (points per line) x 2 (for x and y)
points = np.array([x, y]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)

fig, axs = plt.subplots(2, 1, sharex=True, sharey=True)
# fig = plt.figure(figsize=(8, 6))
# ax = fig.add_subplot(111)

# Create a continuous norm to map from data points to colors
norm = plt.Normalize(dydx.min(), dydx.max())
lc = LineCollection(segments, cmap='viridis', norm=norm)
# Set the values used for colormapping
lc.set_array(dydx)
lc.set_linewidth(2)
line = axs[0].add_collection(lc)
fig.colorbar(line, ax=axs[0])

# Use a boundary norm instead
cmap = ListedColormap(['r', 'g', 'b'])
norm = BoundaryNorm([-1, -0.5, 0.5, 1], cmap.N)
lc = LineCollection(segments, cmap=cmap, norm=norm)
lc.set_array(dydx)
lc.set_linewidth(2)
line = axs[1].add_collection(lc)
fig.colorbar(line, ax=axs[1])

axs[0].set_xlim(df.min()[0] - 500, df.max()[0] + 500)
axs[0].set_ylim(df.min()[1] - 500, df.max()[1] + 500)

plt.show()
