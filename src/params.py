"""
Global parameters for the pipeline
"""
import os

# Name of pipeline, used in Logger
PIPELINE_NAME = "SCRAPE_LONDON_MARATHON"

# Get root directory (with dirname) of the src module
ROOT = os.path.dirname(__file__)

# Mapping of year to no. of pages of results on the website
pages_men = {2021: 1}
pages_women = {2021: 1}

# pages_men = {
#     2011: 23,
#     2012: 24,
#     2013: 23,
#     2014: 23,
#     2015: 24,
#     2016: 24,
#     2017: 24,
#     2018: 24,
#     2019: 29,
#     2020: 22,
#     2021: 25,
# }
# pages_women = {
#     2011: 13,
#     2012: 14,
#     2013: 13,
#     2014: 14,
#     2015: 15,
#     2016: 16,
#     2017: 16,
#     2018: 17,
#     2019: 21,
#     2020: 22,
#     2021: 17,
# }

# Pages is map of sexes to number of pages of results in the search for that year
# This was gathered semi manually, using code like below:
# site_m=requests.get(url1+'1'+url2+'M').text
# site_w=requests.get(url1+'1'+url2+'W').text
# soup_m = BeautifulSoup(site_m,'lxml')
# soup_w = BeautifulSoup(site_w,'lxml')

# m_pages = int(soup_m.find(class_='pages').text[-4:-2])
# w_pages = int(soup_w.find(class_='pages').text[-4:-2])

pages = {"M": pages_men, "W": pages_women}

# pages = {"M": {2021: 1}}

years = [yr for yr in pages_men.keys()]
