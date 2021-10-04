"""
File: london_scraper.py
Project: scrape_london_marathon
Created Date: 7-09-2021
Author: Michael Walshe
-----
Last Modified: 7-09-2021
Modified By: Michael Walshe
-----
Copyright (c) 2021 Amadeus Software Ltd
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
"""


# Setting up required libraries
import pandas as pd
import numpy as np
import requests
import re  # regex
import concurrent.futures  # to allow multithreading
from bs4 import BeautifulSoup, SoupStrainer  # navigate through web pages
# from multiprocessing import Pool, cpu_count  # to allow multiprocessing


def get_results_new(url, sex, year):
    # Function to scrape modern virgin london marathon results page (2020 and 2019)

    results = pd.DataFrame()

    site = requests.get(url).text  # Use requests to get content from site
    strainer = SoupStrainer(
        class_="section-main"
    )  # Soup strainer restricts content to sped up soup
    soup = BeautifulSoup(site, "lxml", parse_only=strainer)  # Parse the html
    # fields = soup.find(class_='section-main')

    # Loop through each row and column to create a list of cells
    my_table = []
    for row in soup.find_all(class_="list-group-item"):
        row_data = []
        for cell in row.find_all(class_="list-field"):
            row_data.append(cell.text)

        # If the row isn't empty, then create a dict of the row to create dataframe from
        # If 2020, then use different row index for Finish
        if len(row_data) > 0 and year != 2020:
            data_item = {
                "Place (Overall)": row_data[0],
                "Place (Gender)": row_data[1],
                "Place (Category)": row_data[2],
                "Name": row_data[3],
                "Sex": sex,
                "Club": row_data[4],
                "Running Number": row_data[5],
                "Category": row_data[6],
                "Finish": row_data[7],
                "Year": year,
            }
            my_table.append(data_item)
        elif len(row_data) > 0 and year == 2020:
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

    df = pd.DataFrame(my_table).iloc[1:]  # Strip table header
    results = results.append(df)  # Append to results

    return results


def get_results_old(url, sex, year):
    # Function to scrape old virgin london marathon results page (2014 to 2018)

    results = pd.DataFrame()  # Set up empty dataframe for results

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
        if len(row_data) > 0 and year != 2014:
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
        elif len(row_data) > 0 and year == 2014:
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

    df = pd.DataFrame(my_table)  # Strip table header
    results = results.append(df)  # Append to results

    return results


def get_results(url):
    # Function choose what results func to apply
    # Used to allow single function for pool.map
    year = int(
        re.search(r"\.com/(\d{4})/", url).group(1)
    )  # Check what year the url is
    sex = re.search(r"sex%5D=(\w)", url).group(1)
    if year >= 2019:
        data = get_results_new(url, sex, year)
    elif year >= 2010:
        data = get_results_old(url, sex, year)
    else:
        data = None
    return data


def get_virgin_urls(sex, pages, year):
    # Get a list of urls, this is needed to be used to apply function to to then use multiprocessing
    urls = ["NaN"] * pages
    if year >= 2019:
        for i in range(len(urls)):
            urls[i] = (
                f"https://results.virginmoneylondonmarathon.com/"
                + str(year)
                + "/?page="
                + str(i + 1)
                + "&event=ALL&num_results=1000&pid=search&pidp=results_nav&search%5Bsex%5D="
                + sex
                + "&search%5Bage_class%5D=%25&search%5Bnation%5D=%25&search_sort=name"
            )

    elif year >= 2014:
        for i in range(len(urls)):
            urls[i] = (
                "https://results.virginmoneylondonmarathon.com/"
                + str(year)
                + "/?page="
                + str(i + 1)
                + "&event=MAS&num_results=1000&pid=list&search%5Bage_class%5D=%25&search%5Bsex%5D="
                + sex
            )

    elif year >= 2010:
        for i in range(len(urls)):
            urls[i] = (
                "https://results.virginmoneylondonmarathon.com/"
                + str(year)
                + "/index.php?page="
                + str(i + 1)
                + "&event=MAS&num_results=1000&pid=search&search%5Bsex%5D="
                + sex
            )

    return urls


if __name__ == "__main__":

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
    pages_men = [23, 24, 23, 23, 24, 24, 24, 24, 29, 22]
    pages_women = [13, 14, 13, 14, 15, 16, 16, 17, 21, 22]
    for i, year in enumerate(range(2011, 2021)):
        w_urls = get_virgin_urls("W", pages_women[i], year)
        m_urls = get_virgin_urls("M", pages_men[i], year)
        urls = urls + m_urls + w_urls\

    # Warning: Takes ~10mins to complete!
    # Trying using multithreading instead of multiprocessing
    MAX_THREADS = 30
    threads = min(MAX_THREADS, len(urls))

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        data = list(executor.map(get_results, urls))

    # Get dataframe from list of df (sep cell to allow for recreation without re-parsing)
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
    LastFirst = results["Name"].str.split(pat=",", n=1, expand=True)
    results["FirstName"], results["LastName"] = LastFirst[1], LastFirst[0]
    # Remove comma from Name column, so that this can be saved as a CSV ----- Must happen after splitting Name into two cols!!
    results["Name"] = results["Name"].str.replace(r"(\,)", "", regex=True)

    # Change W to F for 2020
    results["Sex"] = results["Sex"].str.replace("W", "F")

    # Create DSQ column for did not finish results, to avoid removing info when using nan
    results["DSQ"] = results["Finish"] == "DSQ"

    # Replace non-standard '–' with NaN for missing vals
    results = results.replace("DSQ", np.nan)
    results = results.replace("–", np.nan)
    results = results.replace("", np.nan)

    # Delete odd race number row - gives fastest male/female so is duplicate
    results = results.loc[
        (results["Running Number"] != "RM9999") & (results["Running Number"] != "RF9999")
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

    # Due to an irritating bug with converting objects to Int64, needed to first convert to float and then to int
    results = results.astype(
        {"Place (Overall)": "Int64", "Place (Gender)": "Int64", "Place (Category)": "Int64"}
    )
    results["Finish"] = pd.to_timedelta(results["Finish"])
    results["Finish (Total Seconds)"] = results["Finish"].dt.total_seconds()


    # And save them in a csv
    results.to_csv(
        r"C:\Users\michael.walshe\Documents\Python Projects\scrape_london_marathon\London_Marathon_Big.csv",
        index=False,
        header=True,
    )


