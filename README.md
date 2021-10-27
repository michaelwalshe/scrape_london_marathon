# Scraping the Virgin London Marathon
[![Build and Test](https://github.com/michaelwalshe/scrape_london_marathon/actions/workflows/build-and-test.yml/badge.svg)](https://github.com/michaelwalshe/scrape_london_marathon/actions)


The Virgin London Marathon website provides a webpage showing the results for each year. The underlying dataset is not publicly available, but as there are only slight changes in the search interface each year it is possible to scrape the tables for each year.

Main program is [pipeline.py](/src/pipeline.py), which scrapes and cleans the data in parallel using multithreading, followed by testing the output to ensure it looks as expected. This takes \~15mins to run completely. For a simpler view of the program, or for testing, example_2020_scrape_london_marathon.ipynb just gets the table for the 2020 results without using multithreading.
