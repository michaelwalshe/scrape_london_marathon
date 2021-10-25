import sys

import pytest
import pandas as pd

sys.path.extend(["..", "."])
from src import london_scraper


def test_get_urls():
    pages = {"M": {2020: 1, 2021: 2}}
    actual_urls = london_scraper.generate_virgin_urls(pages)
    expected_urls = [
        "https://results.virginmoneylondonmarathon.com/2021/?page=1&event=ALL&num_"
        "results=1000&pid=search&pidp=results_nav&search%5Bsex%5D=M&search%5Bage_c"
        "lass%5D=%25&search%5Bnation%5D=%25&search_sort=name",
        "https://results.virginmoneylondonmarathon.com/2021/?page=2&event=ALL&num_"
        "results=1000&pid=search&pidp=results_nav&search%5Bsex%5D=M&search%5Bage_c"
        "lass%5D=%25&search%5Bnation%5D=%25&search_sort=name",
    ]

    assert actual_urls == expected_urls


@pytest.mark.xfail("Pandas testing module failing on unexpected characters")
def test_sample_html(requests_mock):
    url = (
        "https://results.virginmoneylondonmarathon.com/2018/?page=1&event=ALL&num_"
        "results=25&pid=search&pidp=results_nav&search%5Bsex%5D=M&search%5Bage_c"
        "lass%5D=%25&search%5Bnation%5D=%25&search_sort=place"
    )

    example_results = pd.read_csv(
        "./tests/inputs/london_2018_exp_output.csv", dtype='object', encoding="utf-8"
    )

    with open('./tests/inputs/Virgin Money London Marathon 2018.html') as f:
        # Replace html request with saved file for test
        requests_mock.get(url, text=f.read())
        results = london_scraper.get_results_table(url, 'M', 2018)

    pd.testing.assert_frame_equal(results, example_results)


if __name__ == "__main__":
    pytest.main()
