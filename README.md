# Scraping the Virgin London Marathon
The Virgin London Marathon website provides a webpage showing the results for each year. The underlying dataset is not publicly available, but as there are only slight changes in the search interface each year it is possible to programmmatically scrape the tables for each year to perform data analysis on.

Currently only example_... works completely as intended, to just scrape the 2020 version of the website, other files are WIP to scrape all other years, and to improve performance by using multiprocessing.

TO DO:
- Improve data cleaning of 2016-2020
- Fix club column on pre 2016, Club is alt-text so use .get?
- Improve performance, multiprocessing/threading? Need to make multiple requests at once
- clean up functions, conglomerate
