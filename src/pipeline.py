from typing import Optional

import pandas as pd
import pytest

from src import (
    params,
    london_scraper,
    london_cleaner,
    london_plotter,
)


def main():
    print("Generating URLS...")
    urls = london_scraper.generate_virgin_urls(params.pages)

    # Warning: Takes ~10mins to complete!
    # Trying using multithreading instead of multiprocessing
    data = london_scraper.run_concurrent_scraping(urls)

    print('Concatenating data')
    results = pd.concat(data)

    print('Cleaning data')
    results = london_cleaner.london_cleaner(results)

    print('"Testing scraper outputs')
    return_code = pytest.main('test_scraper_output.py')

    if return_code != 0:
        raise RuntimeError('Output tests failing, check ....')

    # And save them in a csv
    results.to_csv(
        R"../data/London_Marathon_Big.csv",
        index=False,
        header=True,
    )

    # Now for very basic plots/analysis
    london_plotter.main()


if __name__ == "__main__":
    main()
