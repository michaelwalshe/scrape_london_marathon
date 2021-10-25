import pandas as pd
import numpy as np


def london_cleaner(results: pd.DataFrame) -> pd.DataFrame():
    """Clean the output from scraping the london marathon website.

    Args:
        results: The dataframe of results

    Returns:
        The cleaned dataframe
    """

    # Remove leftover titles
    results["Club"] = results["Club"].str.replace("Club", "", regex=False)
    results["Running Number"] = results["Running Number"].str.replace(
        "Running Number", "", regex=False
    )
    results["Running Number"] = results["Running Number"].str.replace(
        "Runner Number", "", regex=False
    )
    results["Category"] = results["Category"].str.replace("Category", "", regex=False)
    results["Finish"] = results["Finish"].str.replace("Finish", "", regex=False)

    # Extract country groups, like (USA), from Name group
    results["Country"] = results["Name"].str.extract(r"(\([A-Z]{3,}\))")
    # Remove brackets in country
    results["Country"] = results["Country"].str.replace(r"\(|\)", "", regex=True)
    # Remove country group from name column
    results["Name"] = results["Name"].str.replace(r"(\([A-Z]{3}\))", "", regex=True)

    # Split first/lastname into new columns
    results["Name"] = results["Name"].str.replace(r"(»)", "", regex=True)
    results["Name"] = results["Name"].str.replace(r"(\n)", "", regex=True)
    last_first = results["Name"].str.split(pat=",", n=1, expand=True)
    results["FirstName"], results["LastName"] = (
        last_first[1].str.strip(),
        last_first[0].str.strip(),
    )
    # Remove comma from Name column, so that this can be saved as a CSV
    # Must happen after splitting Name into two cols!!
    results["Name"] = results["Name"].str.replace(r"(\,)", "", regex=True).str.strip()

    # Change W to F for 2020
    results["Sex"] = results["Sex"].str.replace("W", "F")

    # Change category NaN to unknown
    results['Category'] = results['Category'].fillna('Unknown')

    # Create DSQ column for did not finish results,
    # to avoid removing info when using nan
    results["DSQ"] = results["Finish"] == "DSQ"

    # Replace non-standard '–' with NaN for missing vals
    results = results.replace("DSQ", np.nan)
    results = results.replace("–", np.nan)
    results = results.replace("", np.nan)

    # Delete odd race number row - gives fastest male/female so is duplicate
    results = results.loc[
        (results["Running Number"] != "RM9999")
        & (results["Running Number"] != "RF9999")
    ]

    results = results.astype(
        {
            "Place (Overall)": "float64",
            "Place (Gender)": "float64",
            "Place (Category)": "float64",
            "Name": str,
            "Sex": str,
            "Club": str,
            "Running Number": str,
            "Category": "category",
            "Year": "Int64",
        }
    )

    # Due to an irritating bug with converting objects to Int64, needed to
    # first convert to float and then to int
    results = results.astype(
        {
            "Place (Overall)": "Int64",
            "Place (Gender)": "Int64",
            "Place (Category)": "Int64",
        }
    )
    results["Finish"] = pd.to_timedelta(results["Finish"])
    results["Finish (Total Seconds)"] = results["Finish"].dt.total_seconds()

    return results
