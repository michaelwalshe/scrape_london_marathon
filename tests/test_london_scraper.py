import sys

import pytest
import pandas as pd

sys.path.append('..')
from src.london_scraper import *

@pytest.fixture()
def get_scraper_output():
    """Can't run the scraper just for data tests, so these check that
    the latest output works. This reads in that data and provides it to
    pytest tests"""
    results = pd.read_csv("./data/London_Marathon_Big_Backup.csv")
    return results

def test_data_attrib(get_scraper_output):
    pass