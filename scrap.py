import json
import logging
import re

from bs4 import BeautifulSoup
from selenium import webdriver
LINK1 = 'http://results.jntuh.ac.in/'
LINK2 = 'http://202.63.105.184/results/'


def get_table_attribute():
    iframe_path = "/html/frameset/frameset/frame[2]"

    driver = webdriver.Firefox(executable_path="drivers/geckodriver")
    driver.get("http://results.jntuh.ac.in/")
    iframe = driver.find_element_by_xpath(iframe_path)
    # driver.switch_to_frame(iframe)
    driver.switch_to.frame(iframe)
    table_xpath = "/html/body/div[2]/table"
    table = driver.find_element_by_xpath(table_xpath)

    return table


def save_table():
    table = get_table_attribute()
    with open("table.html", "w") as f:
        f.write(table.get_attribute("innerHTML"))


def save_exams_json(exams):
    with open('result-links.json', 'w') as f:
        f.write(json.dumps(exams))


def get_all_results():
    """
    within the tablebody, there are table rows
    each row has two table-data elements
    td1:
        a single anchor with an href and has below:
        b -> p -> Exam Description
    td2:
        b -> Date of result declaration
    """

    try:
        table = get_table_attribute()
        table = table.get_attribute('innerHTML')
        soup = BeautifulSoup(table, 'html.parser')
        save_table()
        logging.info("SUCCESS")
    except Exception as e:
        print(e)
        logging.exception("Exception: ", e)
        soup = BeautifulSoup(open("table.html", "r"), 'html.parser')

    rows = soup.find_all("tr")
    regular_exams = []
    supply_exams = []

    for row in rows:
        anchorElement = row.find_all("a")[0]
        link = anchorElement.get("href")
        links = [
            LINK1 + link,
            LINK2 + link
        ]
        re.sub(r'^.*?\?', '', link)
        exam_desc, exam_date = row.find_all("b")
        exam_desc, exam_date = exam_desc.text, exam_date.text

        object = {
            "exam_name": exam_desc,
            "exam_date": exam_date,
            "links": links,
        }

        if "Regular" in exam_desc:
            regular_exams.append(object)
        else:
            supply_exams.append(object)

    all_exams = {
        "regular": regular_exams,
        "supply": supply_exams,
    }

    save_exams_json(all_exams)
    return all_exams
