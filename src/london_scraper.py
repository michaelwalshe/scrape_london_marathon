"""
File: london_scraper.py
Project: scrape_london_marathon
Author: Michael Walshe
"""

import concurrent.futures  # to allow multithreading
import requests
import re
import sys
from typing import Optional, Union

# from multiprocessing import Pool, cpu_count  # to allow multiprocessing

import pandas as pd
from bs4 import BeautifulSoup, SoupStrainer  # navigate through web pages

sys.path.append(".")
from src import params


def get_results_table(url: str, sex: str, year: int) -> pd.DataFrame:
    """Scrape london marathon"""

    # Set parsing values for different years (different page layouts)
    if year == 2021:
        row_indexes = [0, 1, 2, 3, 4, 5, 6, 9]
    elif year == 2014:
        row_indexes = [0, 1, 2, 3, 5, 6, 7, 9]
    else:
        row_indexes = [0, 1, 2, 3, 4, 5, 6, 8]

    site = requests.get(url).text
    # Soup strainer restricts content to speed up soup
    # Annoyingly need to check year several times for different layouts (eval() broke)
    if year >= 2019:
        strainer = SoupStrainer(class_="section-main")
    else:
        strainer = SoupStrainer("tbody")

    soup = BeautifulSoup(site, "lxml", parse_only=strainer)

    # Loop through each row and column to create a list of cells
    my_table = []

    if year >= 2019:
        row_search = soup.find_all(class_="list-group-item")
    else:
        row_search = soup.find_all("tr")

    for row in row_search:
        row_data = []

        if year >= 2019:
            cell_search = row.find_all(class_="list-field")
        else:
            cell_search = row.find_all("td")

        for cell in cell_search:
            alt_text = cell.find("span")
            if year < 2019 and alt_text is not None:
                cell = alt_text["title"]
            else:
                cell = cell.text
            row_data.append(cell)

        # If the row isn't empty, then create a dict of the row to create dataframe from
        if row_data:
            data_item = {
                "Place (Overall)": row_data[row_indexes[0]],
                "Place (Gender)": row_data[row_indexes[1]],
                "Place (Category)": row_data[row_indexes[2]],
                "Name": row_data[row_indexes[3]],
                "Sex": sex,
                "Club": row_data[row_indexes[4]],
                "Running Number": row_data[row_indexes[5]],
                "Category": row_data[row_indexes[6]],
                "Finish": row_data[row_indexes[7]],
                "Year": year,
            }
            my_table.append(data_item)

    results = pd.DataFrame(my_table).iloc[1:]  # Strip table header

    return results


def get_results(url):
    """Function chooses what results func to apply.
    Used to allow single function for pool.map"""

    # Get year and sex from the URL
    year = int(re.search(r"\.com/(\d{4})/", url).group(1))
    sex = re.search(r"sex%5D=(\w)", url).group(1)
    page = re.search(r"page=(.*?)&event=", url).group(1)
    print(f"Getting results for {sex} in {year}, page {page}")

    data = get_results_table(url, sex, year)

    print(f"Finished getting results for {sex} in {year}, page {page}")
    return data


def generate_virgin_urls(
    pages, years: Optional["list[int]"] = None, sexes: Union[list, tuple, None] = None
) -> list:
    """Get a list of urls, this is needed to be used
    to apply function to to then use multiprocessing"""

    if sexes is None:
        sexes = list(pages.keys())

    if years is None:
        years = [yr for yr in pages[sexes[0]].keys() if yr != 2020]

    urls = []
    for sex in sexes:
        urls_single_sex = []
        for year in years:
            pages_of_results = pages[sex][year]
            for i in range(pages_of_results):
                if year >= 2019:
                    url = (
                        "https://results.virginmoneylondonmarathon.com/"
                        + str(year)
                        + "/?page="
                        + str(i + 1)
                        + "&event=ALL&num_results=1000&pid=search&pidp="
                        + "results_nav&search%5Bsex%5D="
                        + sex
                        + "&search%5Bage_class%5D=%25&search"
                        + "%5Bnation%5D=%25&search_sort=name"
                    )

                elif year >= 2014:
                    url = (
                        "https://results.virginmoneylondonmarathon.com/"
                        + str(year)
                        + "/?page="
                        + str(i + 1)
                        + "&event=MAS&num_results=1000&pid=list&search%5"
                        + "Bage_class%5D=%25&search%5Bsex%5D="
                        + sex
                    )

                elif year >= 2010:
                    url = (
                        "https://results.virginmoneylondonmarathon.com/"
                        + str(year)
                        + "/index.php?page="
                        + str(i + 1)
                        + "&event=MAS&num_results=1000&pid=search&search%5Bsex%5D="
                        + sex
                    )
                urls_single_sex.append(url)
        urls.extend(urls_single_sex)
    return urls


def run_concurrent_scraping(urls: "list[str]", MAX_THREADS=30) -> "list[pd.DataFrame]":
    threads = min(MAX_THREADS, len(urls))
    print("Beginning data extract....")
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        data = list(executor.map(get_results, urls))

    return data


def main():
    """Main function that scrapes london marathon website."""

    # Pages is map of sexes to number of pages of results in the search for that year
    # This was gathered semi manually, using code in params.py
    pages = params.pages

    print("Generating URLS...")
    urls = generate_virgin_urls(pages)

    # Warning: Takes ~10mins to complete!
    # Trying using multithreading instead of multiprocessing
    data = run_concurrent_scraping(urls)

    print("Saving data")
    results = pd.concat(data)

    return results


if __name__ == "__main__":
    # years_to_search = [2018, 2019]
    # main(years_to_search)

    # main()
    pages = {"M": {2020: 1, 2021: 2}}

    print(generate_virgin_urls(pages))
