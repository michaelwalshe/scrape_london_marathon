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


def main(filename):
    results = pd.read_csv(
        f"./data/{filename}.csv",
        dtype={
            "Place (Overall)": "Int64",
            "Place (Gender)": "Int64",
            "Place (Category)": "Int64",
            "Name": str,
            "Sex": str,
            "Club": str,
            "Running Number": object,
            "Category": "category",
            "Year": "Int64",
            "Country": str,
            "FirstName": str,
            "LastName": str,
            "DSQ": bool,
            "Finish (Total Seconds)": "float64",
        },
        parse_dates=["Finish"],
    )

    results["Finish"] = pd.to_timedelta(results["Finish"])

    # Basic plotting
    sns.violinplot(data=results, x="Sex", y="Finish (Total Seconds)")
    plt.savefig("./plots/london_violin.png")

    # Try explanatory linear regression with statsmodels
    mod = smf.gls(
        formula='Q("Finish (Total Seconds)") ~ Sex' "+ Category", data=results
    )

    res = mod.fit()

    print(res.summary())

    # Try sklearn linear regression

    # Get label and value arrays of interest, get rid of NaNs
    X = results[["Sex", "Category"]]
    X = X.fillna(X.mode())
    y = results["Finish (Total Seconds)"]
    y = y.fillna(y.mean())

    # Change categorical variables using onehot to 1/0+
    enc = preprocessing.OneHotEncoder()
    X_transform = enc.fit_transform(X)

    # Sample data
    X_train, X_test, y_train, y_test = train_test_split(X_transform, y, test_size=0.2)

    regressor = LinearRegression()
    regressor.fit(X_train, y_train)

    y_pred = regressor.predict(X_test)

    df = pd.DataFrame({"Actual": y_test, "Predicted": y_pred})
    print(df.head())
    # Evaluate algorithm

    print("Mean Absolute Error:", metrics.mean_absolute_error(y_test, y_pred))
    print("Mean Squared Error:", metrics.mean_squared_error(y_test, y_pred))
    print(
        "Root Mean Squared Error:", np.sqrt(metrics.mean_squared_error(y_test, y_pred))
    )


if __name__ == "__main__":
    main()
