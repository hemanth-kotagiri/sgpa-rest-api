import json
import logging
import re


from bs4 import BeautifulSoup

LINK1 = 'http://results.jntuh.ac.in'
LINK2 = 'http://202.63.105.184/results'


class AllResults:
    """ A Class that implements to scrap all links of results """

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logging_formatter = logging.Formatter()
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging_formatter)
    logger.addHandler(stream_handler)

    def __init__(self, driver):

        self.driver = driver
        self.driver.set_page_load_timeout(10)

    def get_table_attribute(self):
        """ Switches to second frameset of webpage and returns table attribute """

        iframe_path = "/html/frameset/frameset/frame[2]"

        self.driver.get("http://results.jntuh.ac.in/")
        iframe = self.driver.find_element_by_xpath(iframe_path)
        self.driver.switch_to.frame(iframe)
        table_xpath = "/html/body/div[2]/table"
        table = self.driver.find_element_by_xpath(table_xpath)

        return table

    def save_table(self):
        """ A method to save the table locally """

        table = self.get_table_attribute()
        with open("table.html", "w") as f:
            f.write(table.get_attribute("innerHTML"))

    def save_exams_json(self, exams):
        """ A method to save exams json object """

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
            self.logger.info("SUCCESS IN SCRAPING DATA")
            self.save_table()
            self.logger.info("SUCCESSFULLY SAVED DATA")
        except Exception as e:
            self.logger.exception("Exception: ", e)
            # Reading the static html that has been saved locally
            soup = BeautifulSoup(open("table.html", "r"), 'html.parser')

        rows = soup.find_all("tr")
        regular_exams = []
        supply_exams = []
        regular_id, supply_id = 0, 0
        for i, row in enumerate(rows):
            anchorElement = row.find_all("a")[0]
            link = anchorElement.get("href")
            params = link.split("&")
            params[0] = re.sub(r'^.*?\?', '', params[0])
            # self.logger.info("PARMS: ", params)
            links = [
                LINK1 + link,
                LINK2 + link
            ]
            re.sub(r'^.*?\?', '', link)
            exam_desc, exam_date = row.find_all("b")
            exam_desc, exam_date = exam_desc.text, exam_date.text

            object = {
                "exam_name": exam_desc,
                "release_date": exam_date,
                "links": links,
            }
            for each_param in params:
                key, value = each_param.split("=")
                object[key] = value

            if "Regular" in exam_desc:
                object["id"] = regular_id
                regular_id += 1
                regular_exams.append(object)
            else:
                object["id"] = supply_id
                supply_id += 1
                supply_exams.append(object)

        all_exams = {
            "regular": regular_exams,
            "supply": supply_exams,
            "id": i
        }

        self.save_exams_json(all_exams)

        return [all_exams, regular_exams, supply_exams]
