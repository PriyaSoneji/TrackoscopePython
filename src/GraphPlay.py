import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

# violin plots
sns.set_theme(style="ticks")
csvfile = 'CSVFiles/OrganismSpeedComp.csv'
df = pd.read_csv(csvfile)

# x1 = df.loc[df.Organism == 'Bursaria', 'Speed (um/s)']
# x2 = df.loc[df.Organism == 'Spirostomum', 'Speed (um/s)']
# x3 = df.loc[df.Organism == 'Actinosphaerium', 'Speed (um/s)']
# x4 = df.loc[df.Organism == 'Blepharisma', 'Speed (um/s)']

fig, ax = plt.subplots()
sns.violinplot(data=df, x='Organism', y='Speed (um/s)', palette="viridis", scale="width", ax=ax)
# ax2 = ax.twinx()
# csvfile = 'CSVFiles/OrganismSpeedComp2.csv'
# df2 = pd.read_csv(csvfile)
# sns.violinplot(data=df2, x='Organism', y='Speed (um/s)', color="#FDE725FF", ax=ax2)
# plt.title('Speed Distributions of Different Organisms')
# # plt.tight_layout()
plt.show()

# histogram
# csvfile = 'CSVFiles/OrganismSpeedComp.csv'
# df = pd.read_csv(csvfile)
#
# x1 = df.loc[df.Organism == 'Bursaria', 'Speed (um/s)']
# x2 = df.loc[df.Organism == 'Spirostomum', 'Speed (um/s)']
# x3 = df.loc[df.Organism == 'Actinosphaerium', 'Speed (um/s)']
# x4 = df.loc[df.Organism == 'Blepharisma', 'Speed (um/s)']
#
# fig, ax = plt.subplots()
#
# sns.histplot(x1, color="#440154FF", label="Bursaria", kde=True, ax=ax)
# sns.histplot(x2, color="#287C8EFF", label="Spirostomum", kde=True, ax=ax)
# sns.histplot(x4, color="#75D054FF", label="Blepharisma", kde=True, ax=ax)
# plt.legend()
# ax2 = ax.twiny()
# sns.histplot(x3, color="#FDE725FF", label="Actinosphaerium", kde=True, ax=ax2)
#
# plt.title('Speed Distributions of Different Organisms')
# plt.legend()
# plt.tight_layout()
# plt.show()
