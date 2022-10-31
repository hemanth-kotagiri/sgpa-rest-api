import logging
import requests
from bs4 import BeautifulSoup


class Service:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logging_formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging_formatter)
    logger.addHandler(stream_handler)

    urls = {
        "1,1": "http://results.jntuh.ac.in/results/resultAction?degree=btech&examCode=1323&etype=r16&type=grade16&result=null&grad=null",
        "1,2": "http://results.jntuh.ac.in/results/resultAction?degree=btech&examCode=1356&etype=r16&type=grade16&result=null&grad=null",
        "2,1": "http://results.jntuh.ac.in/results/resultAction?degree=btech&examCode=1391&etype=r17&type=grade17&result=null&grad=null",
        "2,2": "http://results.jntuh.ac.in/results/resultAction?degree=btech&examCode=1437&etype=r17&type=intgrade&result=null&grad=null",
        "3,1": "http://results.jntuh.ac.in/results/resultAction?degree=btech&examCode=1454&etype=r17&type=intgrade&result=null&grad=null",
        "3,2": "http://results.jntuh.ac.in/results/resultAction?degree=btech&examCode=1502&etype=r17&type=intgrade&result=null&grad=null",
        "4,1": "http://results.jntuh.ac.in/results/resultAction?degree=btech&examCode=1545&etype=r17&type=intgrade&result=null&grad=null",
        "4,2": "http://results.jntuh.ac.in/results/resultAction?degree=btech&examCode=1580&etype=r17&type=intgrade&result=null&grad=null",
    }

    urls2 = {
        "1,1": "http://202.63.105.184/results/resultAction?degree=btech&examCode=1323&etype=r16&type=grade16&type=grade16&result=null&grad=null",
        "1,2": "http://202.63.105.184/results/resultAction?degree=btech&examCode=1356&etype=r16&type=grade16&type=grade16&result=null&grad=null",
        "2,1": "http://202.63.105.184/results/resultAction?degree=btech&examCode=1391&etype=r17&type=grade17&type=grade16&result=null&grad=null",
        "2,2": "http://202.63.105.184/results/resultAction?degree=btech&examCode=1437&etype=r17&type=intgrade&type=grade16&result=null&grad=null",
        "3,1": "http://202.63.105.184/results/resultAction?degree=btech&examCode=1454&etype=r17&type=intgrade&type=grade16&result=null&grad=null",
        "4,1": "http://202.63.105.184/results/resultAction?degree=btech&examCode=1545&etype=r17&type=intgrade&type=grade16&result=null&grad=null",
        "4,2": "http://202.63.105.184/results/resultAction?degree=btech&examCode=1580&etype=r17&type=intgrade&type=grad16&result=null&grad=null",
    }

    def helper(self, url: str, hallticket: str, dob: str) -> list:

        url = url + f"f&htno={hallticket}"
        print(url)

        resp = requests.get(url, timeout=3.0)
        sel_soup = BeautifulSoup(resp.text, 'html.parser')

        # Calling get student and results functions
        student = self.get_student_info(sel_soup)
        results = self.get_results_info(sel_soup)

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

            try:
                return self.helper(self.urls2[year], hallticket, dob)
            except Exception as e:
                self.logger.exception(f"Exception Occoured: {e}")
                return {
                    "error": "JNTUH servers are down"
                }

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

        LINK1 = 'http://results.jntuh.ac.in/results/resultAction?'
        LINK2 = 'http://202.63.105.184/results/resultAction?'

        hallticket = hallticket.upper()
        endpoint = f"degree={degree}&examCode={examCode}"
        if etype:
            endpoint += f"&etype={etype}"
        if type:
            endpoint += f"&type={type}"
        if result:
            endpoint += f"&result={result}"
        else:
            endpoint += f"&result=null"

        url1 = LINK1 + endpoint + "&grad=null"
        url2 = LINK2 + endpoint + "&grad=null"
        try:
            return self.helper(url1, hallticket, dob)
        except Exception as e:
            self.logger.exception(f"Exception occoured: {e}")
            self.logger.info(f"Previous URL : {url1}")

            try:
                return self.helper(url2, hallticket, dob)
            except Exception as e:
                self.logger.exception(f"Exception occoured: {e}")
                return {
                    "error": "JNTUH Servers are down"
                }

    def get_student_info(self, sel_soup) -> dict:
        """ Returns the student information """

        """ tables[0] consists the information regarding the student """

        tables = sel_soup.find_all('table')
        # print(len(tables))
        # print(tables[0].find_all("tr"))

        # Gathering the student information

        data = []
        for element in list(tables[0].find_all("tr")):
            for bTag in element.find_all("b"):
                data.append(bTag.text)

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

        for row in tables[1].find_all("tr"):
            bTags = row.find_all("b")
            if not bTags[0].text.isalnum():
                continue
            current_subject = []
            count = 1
            # table_row has 4 elements: subject code, name, grade, credits else
            # table_row has 7 elements: subject code, name, internal, external, total grade, credits
            for b in bTags:
                if count <= 7:
                    current_subject.append(b.text)
                    count += 1

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
