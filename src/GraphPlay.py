import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

# violin plots
sns.set_theme(style="ticks")
csvfile = 'CSVFiles/OrganismSpeedComp.csv'
df = pd.read_csv(csvfile)
ax = sns.violinplot(data=df, x='Organism', y='Speed', palette="viridis", hue="Organism")
plt.show()

# csvfile = 'CSVFiles/OrganismSpeedComp.csv'
# df = pd.read_csv(csvfile)
#
# x1 = df.loc[df.Organism == 'Bursaria', 'Speed (um/s)']
# x2 = df.loc[df.Organism == 'Spirostomum', 'Speed (um/s)']
# x3 = df.loc[df.Organism == 'Actinosphaerium', 'Speed (um/s)']
# x4 = df.loc[df.Organism == 'Blepharisma', 'Speed (um/s)']
#
# kwargs = dict(hist_kws={'alpha': .6}, kde_kws={'linewidth': 2})
#
# plt.figure(figsize=(10, 7), dpi=80)
# # sns.histplot(data=df, x="Speed (um/s)", hue="Organism", multiple="stack", kde=True)
# sns.histplot(x1, color="#404788FF", label="Bursaria", kde=True)
# sns.histplot(x2, color="#29AF7FFF", label="Spirostomum", kde=True)
# sns.histplot(x3, color="#440154FF", label="Actinosphaerium", kde=True)
# sns.histplot(x4, color="#FDE725FF", label="Blepharisma", kde=True)
#
#
# plt.title('Speed Distributions of Different Organisms')
# plt.legend()
# plt.show()
