import json
import logging
import re
import os
import platform


from bs4 import BeautifulSoup
from selenium import webdriver

LINK1 = 'http://results.jntuh.ac.in/'
LINK2 = 'http://202.63.105.184/results/'


class AllResults:

    driver_file = "drivers/geckodriver" if platform.system() == "Linux" else "drivers/geckodriver.exe"
    driver = None
    chrome_options = webdriver.ChromeOptions()
    firefox_options = webdriver.FirefoxOptions()

    def _init_firefox_driver(self):
        # Arguments for Firefox driver
        self.firefox_options.add_argument("--headless")
        self.firefox_options.add_argument("--no-sandbox")
        self.firefox_options.add_argument("--disable-dev-shm-usage")

        # Firefox Driver
        self.driver = webdriver.Firefox(
            executable_path=os.path.join(os.getcwd(), self.driver_file), firefox_options=self.firefox_options)

    def _init_chrome_driver(self):
        # Specifying the driver options for chrome
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.binary_location = os.environ.get(
            "GOOGLE_CHROME_BIN")
        # Starting the driver
        self.driver = webdriver.Chrome(
            executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=self.chrome_options)

    def __init__(self):

        # st = os.stat(os.path.join(os.getcwd(), self.driver_file))
        # os.chmod(os.path.join(os.getcwd(), self.driver_file),
        # st.st_mode | stat.S_IEXEC)

        # self._init_firefox_driver()
        self._init_chrome_driver()
        self.driver.set_page_load_timeout(10)

    def get_table_attribute(self):
        iframe_path = "/html/frameset/frameset/frame[2]"

        self.driver.get("http://results.jntuh.ac.in/")
        iframe = self.driver.find_element_by_xpath(iframe_path)
        # driver.switch_to_frame(iframe)
        self.driver.switch_to.frame(iframe)
        table_xpath = "/html/body/div[2]/table"
        table = self.driver.find_element_by_xpath(table_xpath)

        return table

    def save_table(self):
        table = self.get_table_attribute()
        with open("table.html", "w") as f:
            f.write(table.get_attribute("innerHTML"))

    def save_exams_json(self, exams):
        with open('result-links.json', 'w') as f:
            f.write(json.dumps(exams))

    def get_all_results(self):
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
            table = self.get_table_attribute()
            table = table.get_attribute('innerHTML')
            soup = BeautifulSoup(table, 'html.parser')
            self.save_table()
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

        self.save_exams_json(all_exams)
        return [all_exams, regular_exams, supply_exams]
