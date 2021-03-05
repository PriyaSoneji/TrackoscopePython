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

print(df.max())
print(df.min())

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111)

# path = mpath.Path(np.column_stack([x, y]))
# verts = path.interpolated(steps=3).vertices
# x, y = verts[:, 0], verts[:, 1]
# z = np.linspace(0, 1, len(x))
# colorline(x, y, z, cmap=plt.get_cmap('jet'), linewidth=2)

for i in range(10):
    colorline(x, y, cmap='cubehelix', linewidth=1)

# plt.plot(x, y)

# plt.scatter(x, y, c=tv)

mplcursors.cursor()

plt.show()
