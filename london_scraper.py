"""
File: london_scraper.py
Project: scrape_london_marathon
Author: Michael Walshe
"""

# Setting up required libraries
import pandas as pd
import numpy as np
import requests
import re
import concurrent.futures  # to allow multithreading
from bs4 import BeautifulSoup, SoupStrainer  # navigate through web pages
from typing import Optional
# from multiprocessing import Pool, cpu_count  # to allow multiprocessing


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
        strainer = SoupStrainer('tbody')

    soup = BeautifulSoup(site, "lxml", parse_only=strainer)

    # Loop through each row and column to create a list of cells
    my_table = []

    if year >= 2019:
        row_search = soup.find_all(class_="list-group-item")
    else:
        row_search = soup.find_all('tr')

    for row in row_search:
        row_data = []

        if year >= 2019:
            cell_search = row.find_all(class_="list-field")
        else:
            cell_search = row.find_all('td')

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


def get_results_new(url: str, sex: str, year: int) -> pd.DataFrame:
    """Function to scrape modern virgin london marathon results page (2019 to 2021)"""

    site = requests.get(url).text
    # Soup strainer restricts content to speed up soup
    strainer = SoupStrainer(class_="section-main")
    soup = BeautifulSoup(site, "lxml", parse_only=strainer)
    # fields = soup.find(class_='section-main')

    # Loop through each row and column to create a list of cells
    my_table = []
    for row in soup.find_all(class_="list-group-item"):
        row_data = []
        for cell in row.find_all(class_="list-field"):
            row_data.append(cell.text)

        # If the row isn't empty, then create a dict of the row to create dataframe from
        if row_data:
            data_item = {
                "Place (Overall)": row_data[0],
                "Place (Gender)": row_data[1],
                "Place (Category)": row_data[2],
                "Name": row_data[3],
                "Sex": sex,
                "Club": row_data[4],
                "Running Number": row_data[5],
                "Category": row_data[6],
                "Finish": row_data[8],
                "Year": year,
            }
            my_table.append(data_item)

    results = pd.DataFrame(my_table).iloc[1:]  # Strip table header

    return results


def get_results_old(url: str, sex: str, year: int) -> pd.DataFrame:
    """Function to scrape old virgin london marathon results page (2014 to 2018)"""

    site = requests.get(url).text  # Use requests to get content from site
    strainer = SoupStrainer("tbody")  # Soup strainer restricts content to sped up soup
    soup = BeautifulSoup(site, "lxml", parse_only=strainer)  # Parse the html

    my_table = []
    for row in soup.find_all("tr"):
        row_data = []
        for cell in row.find_all("td"):
            # Check if cell has alt text, if so use that as data
            alt_text = cell.find("span")
            if alt_text is not None:
                cell = alt_text["title"]
            else:
                cell = cell.text
            row_data.append(cell)

        # If the row isn't empty, then create a dict of the row to create dataframe from
        if row_data and year != 2014:
            data_item = {
                "Place (Overall)": row_data[0],
                "Place (Gender)": row_data[1],
                "Place (Category)": row_data[2],
                "Name": row_data[3],
                "Sex": sex,
                "Club": row_data[4],
                "Running Number": row_data[5],
                "Category": row_data[6],
                "Finish": row_data[8],
                "Year": year,
            }
            my_table.append(data_item)
        elif row_data and year == 2014:
            data_item = {
                "Place (Overall)": row_data[0],
                "Place (Gender)": row_data[1],
                "Place (Category)": row_data[2],
                "Name": row_data[3],
                "Sex": sex,
                "Club": row_data[5],
                "Running Number": row_data[6],
                "Category": row_data[7],
                "Finish": row_data[9],
                "Year": year,
            }
            my_table.append(data_item)

    results = pd.DataFrame(my_table)  # Strip table header

    return results


def get_results(url):
    """Function chooses what results func to apply.
    Used to allow single function for pool.map"""

    # Get year and sex from the URL
    year = int(re.search(r"\.com/(\d{4})/", url).group(1))
    sex = re.search(r"sex%5D=(\w)", url).group(1)
    page = re.search(r"page=(.*?)&event=", url).group(1)
    print(f"Getting results for {sex} in {year}, page {page}")
    # if year >= 2019:
    #     data = get_results_new(url, sex, year)
    # elif year >= 2010:
    #     data = get_results_old(url, sex, year)
    # else:
    #     data = None

    data = get_results_table(url, sex, year)

    print(f"Finished getting results for {sex} in {year}, page {page}")
    return data


def generate_virgin_urls(sex, pages, year):
    """Get a list of urls, this is needed to be used
    to apply function to to then use multiprocessing"""

    urls = ["NaN"] * pages
    if year >= 2019:
        for i in range(pages):
            urls[i] = (
                "https://results.virginmoneylondonmarathon.com/"
                + str(year)
                + "/?page="
                + str(i + 1)
                + "&event=ALL&num_results=1000&pid=search&pidp=results_nav&search%5Bsex%5D="
                + sex
                + "&search%5Bage_class%5D=%25&search%5Bnation%5D=%25&search_sort=name"
            )

    elif year >= 2014:
        for i in range(pages):
            urls[i] = (
                "https://results.virginmoneylondonmarathon.com/"
                + str(year)
                + "/?page="
                + str(i + 1)
                + "&event=MAS&num_results=1000&pid=list&search%5Bage_class%5D=%25&search%5Bsex%5D="
                + sex
            )

    elif year >= 2010:
        for i in range(pages):
            urls[i] = (
                "https://results.virginmoneylondonmarathon.com/"
                + str(year)
                + "/index.php?page="
                + str(i + 1)
                + "&event=MAS&num_results=1000&pid=search&search%5Bsex%5D="
                + sex
            )

    return urls


def main(years: Optional["list[int]"] = None):
    """Main function that scrapes london marathon website.
    If specific years are required, input list of years"""
    urls = []
    # Get no. of pages using technique like
    # Not kept in/included in functions because requests take forever!
    # site_m=requests.get(url1+'1'+url2+'M').text
    # site_w=requests.get(url1+'1'+url2+'W').text
    # soup_m = BeautifulSoup(site_m,'lxml')
    # soup_w = BeautifulSoup(site_w,'lxml')

    # m_pages = int(soup_m.find(class_='pages').text[-4:-2])
    # w_pages = int(soup_w.find(class_='pages').text[-4:-2])
    # print(m_pages, w_pages)
    pages_men = {
        2011: 23,
        2012: 24,
        2013: 23,
        2014: 23,
        2015: 24,
        2016: 24,
        2017: 24,
        2018: 24,
        2019: 29,
        2020: 22,
        2021: 25,
    }
    pages_women = {
        2011: 13,
        2012: 14,
        2013: 13,
        2014: 14,
        2015: 15,
        2016: 16,
        2017: 16,
        2018: 17,
        2019: 21,
        2020: 22,
        2021: 17,
    }

    print("Generating URLS...")
    # Too lazy to setup dataframe for years/pages/gender, need to
    # Check if years to search has been set
    if years is None:
        years = [yr for yr in pages_men.keys() if yr != 2020]  # 2020 has disappeared?

    for year in years:
        w_urls = generate_virgin_urls("W", pages_women[year], year)
        m_urls = generate_virgin_urls("M", pages_men[year], year)
        urls = urls + m_urls + w_urls

    # Warning: Takes ~10mins to complete!
    # Trying using multithreading instead of multiprocessing
    MAX_THREADS = 30
    threads = min(MAX_THREADS, len(urls))
    print("Beginning data extract....")
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        data = list(executor.map(get_results, urls))

    print("Cleaning and saving data...")
    # Get dataframe from list of df
    results = pd.concat(data)

    # Some data cleaning
    # Remove leftover titles
    results["Club"] = results["Club"].str.replace("Club", "", regex=False)
    results["Running Number"] = results["Running Number"].str.replace(
        "Running Number", "", regex=False
    )
    results["Running Number"] = results["Running Number"].str.replace(
        "Runner Number", "", regex=False
    )
    results["Category"] = results["Category"].str.replace("Category", "", regex=False)
    results["Finish"] = results["Finish"].str.replace("Finish", "", regex=False)

    # Extract country groups, like (USA), from Name group
    results["Country"] = results["Name"].str.extract(r"(\([A-Z]{3,}\))")
    # Remove brackets in country
    results["Country"] = results["Country"].str.replace(r"\(|\)", "", regex=True)
    # Remove country group from name column
    results["Name"] = results["Name"].str.replace(r"(\([A-Z]{3}\))", "", regex=True)

    # Split first/lastname into new columns
    results["Name"] = results["Name"].str.replace(r"(»)", "", regex=True)
    results["Name"] = results["Name"].str.replace(r"(\n)", "", regex=True)
    last_first = results["Name"].str.split(pat=",", n=1, expand=True)
    results["FirstName"], results["LastName"] = last_first[1], last_first[0]
    # Remove comma from Name column, so that this can be saved as a CSV
    # Must happen after splitting Name into two cols!!
    results["Name"] = results["Name"].str.replace(r"(\,)", "", regex=True)

    # Change W to F for 2020
    results["Sex"] = results["Sex"].str.replace("W", "F")

    # Create DSQ column for did not finish results,
    # to avoid removing info when using nan
    results["DSQ"] = results["Finish"] == "DSQ"

    # Replace non-standard '–' with NaN for missing vals
    results = results.replace("DSQ", np.nan)
    results = results.replace("–", np.nan)
    results = results.replace("", np.nan)

    # Delete odd race number row - gives fastest male/female so is duplicate
    results = results.loc[
        (results["Running Number"] != "RM9999")
        & (results["Running Number"] != "RF9999")
    ]

    results = results.astype(
        {
            "Place (Overall)": "float64",
            "Place (Gender)": "float64",
            "Place (Category)": "float64",
            "Name": str,
            "Sex": str,
            "Club": str,
            "Running Number": str,
            "Category": "category",
            "Year": "Int64",
        }
    )

    # Due to an irritating bug with converting objects to Int64, needed to
    # first convert to float and then to int
    results = results.astype(
        {
            "Place (Overall)": "Int64",
            "Place (Gender)": "Int64",
            "Place (Category)": "Int64",
        }
    )
    results["Finish"] = pd.to_timedelta(results["Finish"])
    results["Finish (Total Seconds)"] = results["Finish"].dt.total_seconds()

    # And save them in a csv
    results.to_csv(
        r"London_Marathon_Big.csv",
        index=False,
        header=True,
    )


if __name__ == "__main__":
    years_to_search = [2018, 2019]
    main(years_to_search)

    # main()
