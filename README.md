# Scraping the Virgin London Marathon
The Virgin London Marathon website provides a webpage showing the results for each year. The underlying dataset is not publicly available, but as there are only slight changes in the search interface each year it is possible to scrape the tables for each year.

Main program is scrape_london_marathon_multiprocess, which attempts to use multithreading to speed up the requests/parsing, this takes \~15mins to run completely. For a simpler view of the program, or for testing, example_2020_scrape_london_marathon just gets the table for the 2020 results, and so is much quicker.

