import time
import shutil
import sys
import pandas as pd
import pytest

from autologging import logged, traced

sys.path.extend([".", ".."])
from src import (
    params,
    london_scraper,
    london_cleaner,
    london_plotter,
    logger
)

main_log = logger.setup_pipeline_level_logger(
    file_name=f"./logs/example_log_{time.strftime('%Y%m%d-%H%M%S')}.log"
)


@traced
@logged
def main():
    # Setup reporting variables
    start_time = time.strftime("%Y%m%d-%H%M%S")

    main._log.info("Generating URLS...")
    urls = london_scraper.generate_virgin_urls(params.pages)

    # Warning: Takes ~10mins to complete!
    # Trying using multithreading instead of multiprocessing
    # Data is a list of dataframes, one for each year
    data = london_scraper.run_concurrent_scraping(urls)

    main._log.info("Concatenating data...")
    results = pd.concat(data)

    main._log.info("Cleaning data...")
    results = london_cleaner.london_cleaner(results)

    # And save them in a temp csv to then test
    results.to_csv(
        "./data/london_marathon_latest.csv",
        index=False,
        header=True,
    )

    main._log.info("Testing scraper outputs...")
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
    else:
        main._log.info("All tests passing")

    # Rename temp CSV to actual
    shutil.copy(
        "./data/london_marathon_latest.csv",
        f"./data/london_marathon_{start_time}.csv",
    )

    # Now for very basic plots/analysis
    london_plotter.main(f"london_marathon_{start_time}")


if __name__ == "__main__":
    main()
