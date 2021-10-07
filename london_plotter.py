# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'

# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# %%
results = pd.read_csv('./London_Marathon_Big.csv')

# %%
results

# %%
sns.violinplot(data=results, x='Sex', y='Finish (Total Seconds)')
plt.show()
