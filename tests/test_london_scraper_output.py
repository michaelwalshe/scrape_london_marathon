import sys

import pytest
import pandas as pd
import numpy as np
from numpy import dtype
from pandas import Int64Dtype, CategoricalDtype

sys.path.extend(["..", "."])
# from src.london_scraper import *


@pytest.fixture()
def scraper_output():
    """Can't run the scraper just for data tests, so these check that
    the latest output works. This reads in that data and provides it to
    pytest tests"""
    results = pd.read_csv(
        "./data/london_marathon_latest.csv",
        dtype={
            "Place (Overall)": "Int64",
            "Place (Gender)": "Int64",
            "Name": str,
            "Sex": str,
            "Club": str,
            "Running Number": object,
            "Category": CategoricalDtype(
                categories=[
                    '18-39',
                    '40-44',
                    '45-49',
                    '50-54',
                    '55-59',
                    '60-64',
                    '65-69',
                    '70+',
                    '70-74',
                    '75-79',
                    '80-84',
                    '85+',
                    '80+',
                    'Unknown'
                ],
                ordered=False,
            ),
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

    return results


def test_output_attributes(scraper_output):
    results = scraper_output
    exp_cols = [
        "Place (Overall)",
        "Place (Gender)",
        "Place (Category)",
        "Name",
        "Sex",
        "Club",
        "Running Number",
        "Category",
        "Finish",
        "Year",
        "Country",
        "FirstName",
        "LastName",
        "DSQ",
        "Finish (Total Seconds)",
    ]

    exp_dtypes = pd.Series(
        {
            "Place (Overall)": Int64Dtype(),
            "Place (Gender)": Int64Dtype(),
            "Place (Category)": dtype("float64"),
            "Name": dtype("O"),
            "Sex": dtype("O"),
            "Club": dtype("O"),
            "Running Number": dtype("O"),
            "Category": CategoricalDtype(
                categories=[
                    '18-39',
                    '40-44',
                    '45-49',
                    '50-54',
                    '55-59',
                    '60-64',
                    '65-69',
                    '70+',
                    '70-74',
                    '75-79',
                    '80-84',
                    '85+',
                    '80+',
                    'Unknown'
                ],
                ordered=False,
            ),
            "Finish": dtype("<m8[ns]"),
            "Year": Int64Dtype(),
            "Country": dtype("O"),
            "FirstName": dtype("O"),
            "LastName": dtype("O"),
            "DSQ": dtype("bool"),
            "Finish (Total Seconds)": dtype("float64"),
        }
    )

    exp_rows_min = 1000  # One sex for one year should give at least this many

    assert exp_cols == list(results.columns), "Expected columns not found"
    assert exp_rows_min <= results.shape[0], "Less than minimum expected number of rows"

    assert exp_dtypes.values.tolist() == results.dtypes.values.tolist()


def test_category_values(scraper_output):
    results = scraper_output

    exp_categories = [
        '18-39',
        '40-44',
        '45-49',
        '50-54',
        '55-59',
        '60-64',
        '65-69',
        '70+',
        '70-74',
        '75-79',
        '80-84',
        '85+',
        '80+',
        'Unknown',
        np.nan
    ]
    actual_categories = results["Category"].unique().tolist()

    assert all(
        cat in exp_categories for cat in actual_categories
    ), f"Unexpected Category value in {actual_categories}"


def test_sex_values(scraper_output):
    results = scraper_output

    exp_sex_vals = ["M", "F"]
    actual_sex_vals = results["Sex"].unique().tolist()

    assert all(
        sex in exp_sex_vals for sex in actual_sex_vals
    ), "Unexpected value for Sex"


def test_finish_values(scraper_output):
    results = scraper_output

    exp_finish_max = pd.Timedelta("1 days 0:00:00")
    exp_finish_min = pd.Timedelta("0 days 1:30:00")

    finish_max = results["Finish"].max()
    finish_min = results["Finish"].min()

    assert (
        finish_max < exp_finish_max
    ), "Actual Finish time maximum greater than expected"
    assert (
        finish_min > exp_finish_min
    ), "Actual Finish time mainimum greater than expected"


def test_year_values(scraper_output):
    results = scraper_output

    exp_year_vals = list(range(2011, 2022))
    actual_year_vals = list(results["Year"].unique())

    assert all(
        year in exp_year_vals for year in actual_year_vals
    ), "Unexpected value for Year"


if __name__ == "__main__":
    pytest.main()
