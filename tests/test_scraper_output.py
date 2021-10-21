import sys

import pytest
import pandas as pd

sys.path.append('..')
from src.london_scraper import *

@pytest.fixture()
def scraper_output():
    """Can't run the scraper just for data tests, so these check that
    the latest output works. This reads in that data and provides it to
    pytest tests"""
    results = pd.read_csv(
        "../data/London_Marathon_Big_Backup.csv",
        dtype={
            "Place (Overall)": "Int64",
            "Place (Gender)": "Int64",
            "Name": str,
            "Sex": str,
            "Club": str,
            "Running Number": object,
            "Category": "category",
            'Finish': "timedelta64",
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


def test_data_attrib(scraper_output):
    pass
