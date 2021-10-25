import sys

import pytest
import pandas as pd
from numpy import dtype
from pandas import Int64Dtype, CategoricalDtype

sys.path.extend(["..", "."])
from src.london_cleaner import london_cleaner


def test_london_cleaner():
    unclean_input = pd.DataFrame.from_dict(
        {
            "Place (Overall)": [12547, 34146],
            "Place (Gender)": [9390, 20833],
            "Place (Category)": [4345, 3132],
            "Name": ["»A Smith, Matthew (GBR) \n", "»Aalders, Jennifer (GBR) \n"],
            "Sex": ["M", "W"],
            "Club": ["Lymm Runners", "Tynny Trotters"],
            "Running Number": ["Runner Number40546", "Runner Number23235"],
            "Category": ["18-39", "45-49"],
            "Finish": ["0 days 03:59:33", "0 days 06:22:20"],
            "Year": [2021, 2021],
        }
    )

    exp_output = pd.DataFrame.from_dict(
        {
            "Place (Overall)": [12547, 34146],
            "Place (Gender)": [9390, 20833],
            "Place (Category)": [4345, 3132],
            "Name": ["A Smith Matthew", "Aalders Jennifer"],
            "Sex": ["M", "F"],
            "Club": ["Lymm Runners", "Tynny Trotters"],
            "Running Number": ["40546", "23235"],
            "Category": ["18-39", "45-49"],
            "Finish": [
                pd.Timedelta("0 days 03:59:33"),
                pd.Timedelta("0 days 06:22:20"),
            ],
            "Year": [2021, 2021],
            "Country": ["GBR", "GBR"],
            "FirstName": ["Matthew", "Jennifer"],
            "LastName": ["A Smith", "Aalders"],
            "DSQ": [False, False],
            "Finish (Total Seconds)": [14373.0, 22940.0],
        }
    ).astype(
        {
            "Place (Overall)": Int64Dtype(),
            "Place (Gender)": Int64Dtype(),
            "Place (Category)": Int64Dtype(),
            "Name": dtype("O"),
            "Sex": dtype("O"),
            "Club": dtype("O"),
            "Running Number": dtype("O"),
            "Category": CategoricalDtype(
                categories=[
                    "18-39",
                    "40-44",
                    "45-49",
                    "50-54",
                    "55-59",
                    "60-64",
                    "65-69",
                    "70-74",
                    "75-79",
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

    actual_output = london_cleaner(unclean_input)

    pd.testing.assert_frame_equal(actual_output, exp_output, check_categorical=False)


if __name__ == "__main__":
    pytest.main()
