import os
import logging
import sys
from urllib.parse import unquote
from bs4 import BeautifulSoup
from selenium import webdriver


def scrape_html(src_url):
    driver = webdriver.Chrome()  # Open Chrome Instance to load the link
    driver.get(src_url)

    # Run this script to get the html code after loading all scripts
    html = driver.execute_script("return document.documentElement.outerHTML")
    soup = BeautifulSoup(html, "html.parser")

    # get list of all html anchors
    anchors = soup.find_all("a")  # print(f"Number of Anchor tags: {len(anchors)}")
    return anchors, html


def scrape_url(anchors):
    uris_set = set()  # Use set to avoid duplicates in the array

    for each in anchors:
        try:  # if anchor tag does not have href link, skip tag
            href = each["href"]
        except:
            continue
        uris_set.add(href)
    return uris_set


def write_to_files(file_path, uris_set):
    if not os.path.isdir(os.path.dirname(file_path)):
        try:
            os.makedirs(os.path.dirname(file_path))
            print(os.path.dirname(file_path), ": Directory Created")
        except OSError as excep:
            print(excep.errno, ": ", excep.strerror)

    abs_url_set = set()  # Create

    for each in uris_set:
        if "http" in unquote(each) or "https" in unquote(each):
            if "#" in unquote(each):
                abs_url_set.add(str(each).split("#", 1)[0])
                # Remove duplicate navigation of same URI with http/https tag
            else:
                abs_url_set.add(str(each).rstrip("/"))
                # Remove / at the end to avoid duplicate URI scenario
        else:
            if "#" in unquote(each):
                #  Remove duplicate navigation of same URI without http/https; avoid blank entries
                abs_url_set.add(str("https://www.census.gov" + str(each).split("#", 1)[0]))

            else:
                # concatenate full address for relative links
                abs_url_set.add(str("https://www.census.gov" + each).rstrip("/"))

    with open(file_path, "w+") as writeurls:
        for each in list(abs_url_set):
            writeurls.write(each)
            writeurls.write("\n")
    writeurls.close()


def write_html_code(html_path, html_code):
    if not os.path.isdir(os.path.dirname(html_path)):
        try:
            os.makedirs(os.path.dirname(html_path))
            print(os.path.dirname(html_path), ": Directory Created")
        except OSError as excep:
            print(excep.errno, ": ", excep.strerror)

    with open(html_path, "w+", encoding="utf-8") as writehtml:
        writehtml.write(html_code)
    writehtml.close()


def main(url):
    logger = logging.getLogger(__name__)
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    logger.info("Getting all URIs from US Census Bureau - Current Estimates")

    url_file_dir = os.path.join(os.path.curdir, "Extracted Files")
    url_file_path = os.path.join(url_file_dir, "USCensus-CurrentEst-ScrapedWebLinks.csv")

    try:
        anchors, html = scrape_html(url)
        urls = scrape_url(anchors)  # Scrape URIs and save to CSV file
        logger.info("All URIs generated")
    except EnvironmentError as ex:
        logger.error("There was an error while scraping for Unique URIs", ex)
        sys.exit()  # Exit script if any issue with the function calls

    logger.info("Writing URIs to the file")

    try:
        write_to_files(url_file_path, urls)
    except EnvironmentError as ex:
        logger.error("There was an error creating CSV file for Unique URIs", ex)
        sys.exit()

    logger.info("File with unique URIs generated successfully")
    html_file_path = os.path.join(url_file_dir, "USCensus-CurrentEst-HtmlCode.html")
    logger.info("Writing HTML Code to the file")

    try:
        write_html_code(html_file_path, html)  # Write the HTML source from the website to HTML file
        logger.info("File with html code generated successfully")
    except EnvironmentError as ex:
        logger.error("There was an error creating HTML file for Current Estimates site", ex)
        sys.exit()

    logger.info("Script Completed successfully")


if __name__ == "__main__":
    main("http://www.census.gov/programs-surveys/popest.html")
