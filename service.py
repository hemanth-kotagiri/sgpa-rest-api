import time
import os
import stat
import requests
import urllib3
from bs4 import BeautifulSoup
from selenium import webdriver
import platform

# TODO : Initialize the driver without window


class Crawler:

    urls = {
        "1,1": "http://results.jntuh.ac.in/jsp/SearchResult.jsp?degree=btech&examCode=1323&etype=r16&type=grade16",
        "1,2": "http://results.jntuh.ac.in/jsp/SearchResult.jsp?degree=btech&examCode=1356&etype=r16&type=grade16",
        "2,1": "http://results.jntuh.ac.in/jsp/SearchResult.jsp?degree=btech&examCode=1391&etype=r17&type=grade17",
        "2,2": "http://results.jntuh.ac.in/jsp/SearchResult.jsp?degree=btech&examCode=1437&etype=r17&type=intgrade",
    }
    driver_file = "drivers/geckodriver" if platform.system() == "Linux" else "drivers/geckodriver.exe"
    driver = None
    chrome_options = webdriver.ChromeOptions()

    def __init__(self):
        # Specifying the driver options
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.binary_location = os.environ.get(
            "GOOGLE_CHROME_BIN")

        st = os.stat(os.path.join(os.getcwd(), self.driver_file))
        os.chmod(os.path.join(os.getcwd(), self.driver_file),
                 st.st_mode | stat.S_IEXEC)

        # Starting the driver
        self.driver = webdriver.Chrome(
            executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=self.chrome_options)

    def get_result(self, hallticket, dob, year):

        hallticket = hallticket.upper()
        url = self.urls[year]
        # Returns the json object of results
        self.driver.get(url)

        # Getting the captcha value
        captcha_val = self.driver.execute_script(
            "return document.getElementById('txtCaptcha').value")
        hall_pass = "document.getElementById('htno').value = '{}'".format(
            hallticket)
        date_pass = "document.getElementById('datepicker').value = '{}'".format(
            dob)
        pass_str = "document.getElementById('txtInput').value = '{}'".format(
            captcha_val)

        self.driver.execute_script(pass_str)
        self.driver.execute_script(date_pass)
        self.driver.execute_script(hall_pass)

        submit_button_xpath = '//*[@id="myForm"]/div/table/tbody/tr[5]/td[3]/input'

        submit = self.driver.find_element_by_xpath(submit_button_xpath)
        submit.click()

        # After submitting the form
        next_url = self.driver.current_url

        # print(next_url)

        sel_html = self.driver.execute_script(
            "return document.documentElement.outerHTML")

        # print(sel_html)
        sel_soup = BeautifulSoup(sel_html, 'html.parser')

        result = (sel_soup.prettify())

        subjects = []
        grades = []
        name = ""

        tables = sel_soup.find_all('table')

        """ tables[0] consists the information regarding the student """
        """ tables[1] consists the subject code, subject name, grade and credits"""

        # Gathering the student information

        data = []
        for element in list(tables[0].tbody):
            for row in element:
                for td in row:
                    for b in td:
                        if type(b) != str:
                            data.append(str(b.string).replace("\n", "").strip())

        student = dict(zip([data[i].replace(":", "") for i in range(len(data))
                            if i % 2 == 0], [data[j] for j in range(1,
                                                                    len(data))
                                             if j % 2 != 0]))

        results = []

        for element in list(tables[1].tbody)[1:]:
            current_subject = []
            for table_row in element:
                for b in table_row:
                    if type(b) != str:
                        # table_row has 4 elements: subject code, name, grade, credits else
                        # table_row has 7 elements: subject code, name, internal, external, total grade, credits
                        current_subject.append(b.text)

            if not current_subject:
                continue

            subject_object = {}
            if current_subject and len(current_subject) == 4:
                subject_object["subject_code"] = current_subject[0]
                subject_object["subject_name"] = current_subject[1]
                subject_object["grade_earned"] = current_subject[2]
                subject_object["subject_credits"] = current_subject[3]
            else:
                subject_object["subject_code"] = current_subject[0]
                subject_object["subject_name"] = current_subject[1]
                subject_object["internal_marks"] = current_subject[2]
                subject_object["external_marks"] = current_subject[3]
                subject_object["total_marks"] = current_subject[4]
                subject_object["grade_earned"] = current_subject[5]
                subject_object["subject_credits"] = current_subject[6]

            results.append(subject_object)

        self.driver.back()

        return [student, results]
