import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.gridspec as gridspec
import pandas as pd
import mplcursors


# reference code: https://matplotlib.org/stable/gallery/lines_bars_and_markers/multicolored_line.html
# color map reference: https://matplotlib.org/stable/tutorials/colors/colormaps.html
# decent cmap types - 'turbo', 'gist_rainbow', 'cool', 'hsv'

# function to change timestamp to seconds
def get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


# read csv file and create pandas dataframe
csvfile = 'CSVFiles/Stentor2.csv'
df = pd.read_csv(csvfile)

# variables and lists needed
timev = []
mint = get_sec(df.min()[2])
maxt = get_sec(df.max()[2])
timediff = maxt - mint
speed = []
x = []
y = []

# gets x and y values
for index, row in df.iterrows():
    x.append(row['xval'])
    y.append(row['yval'])

# converts the list of time stamp to list of seconds starting from zero
for index, row in df.iterrows():
    timev.append((get_sec(row['time'])) - mint)

# timeexp = list(range(0, timev[-1] + 1))
timeexp = [0]

# calculates speed
count = 0
for t in timev:
    changet = timev[count + 1] - timev[count]
    if changet >= 30:
        # if 30 second gap in time stamps then speed is assumed to be zero
        for j in range(int(timev[count + 1] - timev[count])):
            speed.append(0)
            timeexp.append(timeexp[-1] + 30)
    elif changet == 0:
        # if entries with same timestamp just duplicate previous entry (avoids divide by zero error)
        speed.append(speed[-1])
        timeexp.append(timeexp[-1])
    else:
        # calculate speed based on change in distance/change in time
        distance = np.sqrt(((x[count + 1] - x[count]) ** 2) + ((y[count + 1] - y[count]) ** 2))
        speed.append(round((distance / changet), 2))
        timeexp.append(timeexp[-1] + changet)

    count = count + 1

    if count + 1 >= len(x):
        break

speed.append(speed[-1])

# define plots
fig = plt.figure(figsize=(8, 6), facecolor='lightgrey', constrained_layout=True)
spec = fig.add_gridspec(2, 2)
ax = fig.add_subplot(spec[0, 0], xlabel='X-Movement (μm)', ylabel='Y-Movement (μm)', title='Position vs Time',
                     navigate=False, fc='lightgrey')
ax1 = fig.add_subplot(spec[1, :], xlabel='Time (s)', ylabel='Speed (μm/s)', title='Speed vs Time', navigate=False,
                      fc='lightgrey')
ax2 = fig.add_subplot(spec[0, 1], xlabel='X-Movement (μm)', ylabel='Y-Movement (μm)', title='Position vs Speed',
                      navigate=False,
                      fc='lightgrey')

# Create a set of line segments so that we can color them individually
points1 = np.array([x, y]).T.reshape(-1, 1, 2)
segments1 = np.concatenate([points1[:-1], points1[1:]], axis=1)
# Define gradient and plot pos vs time graph
norm1 = plt.Normalize(min(timev), max(timev))
lc1 = LineCollection(segments1, cmap='hsv', norm=norm1)
lc1.set_array(np.array(timev))
lc1.set_linewidth(1)
line1 = ax.add_collection(lc1)
fig.colorbar(line1, ax=ax)
ax.set_xlim(df.min()[0] - 200, df.max()[0] + 200)
ax.set_ylim(df.min()[1] - 200, df.max()[1] + 200)

# Create a set of line segments so that we can color them individually
points2 = np.array([timeexp, speed]).T.reshape(-1, 1, 2)
segments2 = np.concatenate([points2[:-1], points2[1:]], axis=1)
# Define gradient and plot speed vs time graph
norm2 = plt.Normalize(min(speed), max(speed))
lc2 = LineCollection(segments2, cmap='hsv', norm=norm2)
lc2.set_array(np.array(speed))
lc2.set_linewidth(1)
line2 = ax1.add_collection(lc2)
fig.colorbar(line2, ax=ax1)
ax1.set_xlim(timeexp[0] - 200, timeexp[-1] + 200)
ax1.set_ylim(speed[0] - 5, speed[-1] + 5)

# Create a set of line segments so that we can color them individually
points3 = np.array([x, y]).T.reshape(-1, 1, 2)
segments3 = np.concatenate([points3[:-1], points3[1:]], axis=1)
# Define gradient and plot pos vs speed graph
norm3 = plt.Normalize(min(speed), max(speed))
lc3 = LineCollection(segments3, cmap='turbo', norm=norm3)
lc3.set_array(np.array(speed))
lc3.set_linewidth(1)
line3 = ax2.add_collection(lc3)
fig.colorbar(line3, ax=ax2)
ax2.set_xlim(df.min()[0] - 200, df.max()[0] + 200)
ax2.set_ylim(df.min()[1] - 200, df.max()[1] + 200)

# show plots
mplcursors.cursor()
plt.show()
