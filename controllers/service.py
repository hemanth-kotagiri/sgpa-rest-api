import logging
from bs4 import BeautifulSoup


class Service:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logging_formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging_formatter)
    logger.addHandler(stream_handler)

    urls = {
        "1,1": "http://results.jntuh.ac.in/results/jsp/SearchResult.jsp?degree=btech&examCode=1323&etype=r16&type=grade16",
        "1,2": "http://results.jntuh.ac.in/results/jsp/SearchResult.jsp?degree=btech&examCode=1356&etype=r16&type=grade16",
        "2,1": "http://results.jntuh.ac.in/results/jsp/SearchResult.jsp?degree=btech&examCode=1391&etype=r17&type=grade17",
        "2,2": "http://results.jntuh.ac.in/results/jsp/SearchResult.jsp?degree=btech&examCode=1437&etype=r17&type=intgrade",
        "3,1": "http://results.jntuh.ac.in/results/jsp/SearchResult.jsp?degree=btech&examCode=1454&etype=r17&type=intgrade",
        "3,2": "http://results.jntuh.ac.in/results/jsp/SearchResult.jsp?degree=btech&examCode=1502&etype=r17&type=intgrade",
    }

    urls2 = {
        "1,1": "http://202.63.105.184/results/jsp/SearchResult.jsp?degree=btech&examCode=1323&etype=r16&type=grade16",
        "1,2": "http://202.63.105.184/results/jsp/SearchResult.jsp?degree=btech&examCode=1356&etype=r16&type=grade16",
        "2,1": "http://202.63.105.184/results/jsp/SearchResult.jsp?degree=btech&examCode=1391&etype=r17&type=grade17",
        "2,2": "http://202.63.105.184/results/jsp/SearchResult.jsp?degree=btech&examCode=1437&etype=r17&type=intgrade",
        "3,1": "http://202.63.105.184/results/jsp/SearchResult.jsp?degree=btech&examCode=1454&etype=r17&type=intgrade",
        "3,2": "http://202.63.105.184/results/jsp/SearchResult.jsp?degree=btech&examCode=1502&etype=r17&type=intgrade",
    }

    def __init__(self, driver):
        self.driver = driver
        self.driver.set_page_load_timeout(10)

    def helper(self, url: str, hallticket: str, dob: str) -> list:

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

        # Creating the soup object for the result page
        sel_html = self.driver.execute_script(
            "return document.documentElement.outerHTML")

        sel_soup = BeautifulSoup(sel_html, 'html.parser')

        # Calling get student and results functions
        student = self.get_student_info(sel_soup)
        results = self.get_results_info(sel_soup)
        self.driver.back()

        return [student, results]

    def get_result(self, hallticket: str, dob: str, year: str) -> list:
        """Returns the json object of results
        parameters:
            hallticket(str) -- student's hallticket number
            dob(str) -- student's date of birth
            year(str) -- comma saperated year and semester value. eg: 1,1
        """
        hallticket = hallticket.upper()
        url = self.urls[year]
        try:
            return self.helper(url, hallticket, dob)

        except Exception as e:
            self.logger.exception(f"Exception occoured: {e}")
            self.logger.info(f"Previous URL : {url}")

            return self.helper(self.urls2[year], hallticket, dob)

    def get_result_with_url(self, hallticket: str, dob: str, degree: str,
                            examCode: str, etype: str, type: str, result: str) -> list:
        """ A method to fetch the results given the paremeters as a JSON object
        parameters:
            hallticket(str)
            dob(str)
            degree(str)
            examCode(str)
            etype(str)
            type(str)
            result(str)
        """

        LINK1 = 'http://results.jntuh.ac.in/jsp/SearchResult.jsp?'
        LINK2 = 'http://202.63.105.184/results/jsp/SearchResult.jsp?'

        hallticket = hallticket.upper()
        endpoint = f"degree={degree}&examCode={examCode}"
        if etype:
            endpoint += f"&etype={etype}"
        if type:
            endpoint += f"&type={type}"
        if result:
            endpoint += f"&result={result}"
        url1 = LINK1 + endpoint
        url2 = LINK2 + endpoint
        try:
            return self.helper(url1, hallticket, dob)
        except Exception as e:
            self.logger.exception(f"Exception occoured: {e}")
            self.logger.info(f"Previous URL : {url1}")

            return self.helper(url2, hallticket, dob)

    def get_student_info(self, sel_soup) -> dict:
        """ Returns the student information """

        """ tables[0] consists the information regarding the student """

        tables = sel_soup.find_all('table')

        # Gathering the student information

        data = []
        for element in list(tables[0].tbody):
            for row in element:
                for td in row:
                    for b in td:
                        if type(b) != str:
                            data.append(
                                str(b.string).replace("\n", "").strip())

        student = dict(zip([data[i].replace(":", "") for i in range(len(data))
                            if i % 2 == 0], [data[j] for j in range(1,
                                                                    len(data))
                                             if j % 2 != 0]))

        return student

    def get_results_info(self, sel_soup):
        """ A method to obtain the results object 
        tables[1] consists the subject code, subject name, grade and credits
        """

        tables = sel_soup.find_all('table')
        results = []

        for element in list(tables[1].tbody)[1:]:
            current_subject = []
            count = 1
            for table_row in element:
                for b in table_row:
                    if type(b) != str and count <= 7:
                        count += 1
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
                subject_object["grade_earned"] = current_subject[5]
                subject_object["subject_credits"] = current_subject[6]
                subject_object["internal_marks"] = current_subject[2]
                subject_object["external_marks"] = current_subject[3]
                subject_object["total_marks"] = current_subject[4]

            results.append(subject_object)

        return results
