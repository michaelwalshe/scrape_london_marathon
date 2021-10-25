import sys

import pytest

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


if __name__ == "__main__":
    pytest.main()
