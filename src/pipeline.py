import time
import shutil
import sys
import pandas as pd
import pytest

sys.path.extend([".", ".."])
from src import (
    params,
    london_scraper,
    london_cleaner,
    london_plotter,
)


def main():
    # Setup reporting variables
    start_time = time.strftime("%Y%m%d-%H%M%S")

    print("Generating URLS...")
    urls = london_scraper.generate_virgin_urls(params.pages)

    # Warning: Takes ~10mins to complete!
    # Trying using multithreading instead of multiprocessing
    # Data is a list of dataframes, one for each year
    data = london_scraper.run_concurrent_scraping(urls)

    print("Concatenating data...")
    results = pd.concat(data)

    print("Cleaning data...")
    results = london_cleaner.london_cleaner(results)

    # And save them in a temp csv to then test
    results.to_csv(
        "./data/london_marathon_latest.csv",
        index=False,
        header=True,
    )

    print("Testing scraper outputs...")
    return_code = pytest.main(
        [
            "./tests/test_london_scraper_output.py",
            f"--html=./tests/reports/scraper_report_{start_time}.html",
            "--self-contained-html",
        ]
    )
    if return_code != 0:
        raise RuntimeError(
            f"Output tests failing, check scraper_report_{start_time}.html"
        )
    # If no failing tests then pass

    # Rename temp CSV to actual
    shutil.copy(
        "./data/london_marathon_latest.csv",
        f"./data/london_marathon_{start_time}.csv",
    )

    # Now for very basic plots/analysis
    london_plotter.main(f"london_marathon_{start_time}")


if __name__ == "__main__":
    main()
