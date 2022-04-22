import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

sns.set_theme(style="ticks")
csvfile = 'CSVFiles/Pseudopods.csv'
df = pd.read_csv(csvfile)
ax = sns.violinplot(x="Locomotion", y="Pseudopods", data=df, palette="viridis")
plt.show()
