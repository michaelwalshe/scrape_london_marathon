# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.formula.api as smf
# import statsmodels.api as sm

from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics

# %%

# Read in dataset, with dtypes set ready for analyis

results = pd.read_csv(
    '../data/London_Marathon_Big_Backup.csv',
    dtype={
        'Place (Overall)': "float64",  # Declare ints as floats for statsmodels
        'Place (Gender)': "float64",
        'Name': str,
        'Sex': str,
        'Club': str,
        'Running Number': object,  # Needs to be object because of runner "ROSS BULL?"
        'Category': "category",
        # 'Finish': "timedelta64",
        'Year': "float64",
        'Country': str,
        'FirstName': str,
        'LastName': str,
        'DSQ': bool,
        'Finish (Total Seconds)': "float64"
    },
    parse_dates=['Finish']
)

results["Finish"] = pd.to_timedelta(results["Finish"])

# %%

# Check imports
results

# %%

# Basic plotting
sns.violinplot(data=results, x='Sex', y='Finish (Total Seconds)')
plt.show()

# %%

# Try explanatory linear regression with statsmodels
mod = smf.gls(
    formula='Q("Finish (Total Seconds)") ~ Sex'
            '+ Category',
    data=results
)

res = mod.fit()

print(res.summary())

# %%

# Try sklearn linear regression

# Get label and value arrays of interest, get rid of NaNs
X = results[['Sex', 'Category']]
X = X.fillna(X.mode())
y = results['Finish (Total Seconds)']
y = y.fillna(y.mean())

# Change categorical variables using onehot to 1/0+
enc = preprocessing.OneHotEncoder()
X_transform = enc.fit_transform(X)

# Sample data
X_train, X_test, y_train, y_test = train_test_split(X_transform, y, test_size=0.2)


regressor = LinearRegression()
regressor.fit(X_train, y_train)

y_pred = regressor.predict(X_test)

df = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})
df

# %%

# Evaluate algorithm

print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, y_pred))
print('Mean Squared Error:', metrics.mean_squared_error(y_test, y_pred))
print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, y_pred)))
