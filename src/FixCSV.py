import numpy as np
from datetime import datetime
import pandas as pd
import time

# read csv file and create pandas dataframe
csvfile = 'CSVFiles/Stentor2.csv'
df = pd.read_csv(csvfile)

# variables and lists needed
times = []
x = []
y = []
newtimes = []

# gets x and y values and timestamps
for index, row in df.iterrows():
    x.append(round((row['xval']), 3))
    y.append(round((row['yval']), 3))
    times.append(row['time'])

initial = t = sum(j * int(p) for j, p in zip([3600, 60, 1], times[0].split(":")))

for t in times:
    w = sum(j * int(p) for j, p in zip([3600, 60, 1], t.split(":")))
    newtimes.append(w - initial)

print(newtimes)

df = pd.DataFrame(data={"xval": x, "yval": y, "time": newtimes})
df.to_csv(csvfile, sep=',', index=False)
