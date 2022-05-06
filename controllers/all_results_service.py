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
    logging_formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging_formatter)
    logger.addHandler(stream_handler)

    def __init__(self, driver):

        self.driver = driver
        self.driver.set_page_load_timeout(10)

    def get_table_attribute(self) -> None:
        """ Switches to second frameset of webpage and returns table attribute """

        iframe_path = "/html/frameset/frameset/frame[2]"

        self.driver.get("http://results.jntuh.ac.in/")
        iframe = self.driver.find_element_by_xpath(iframe_path)
        self.driver.switch_to.frame(iframe)
        table_xpath = "/html/body/div[2]/table"
        table = self.driver.find_element_by_xpath(table_xpath)

        return table

    def get_notifiations(self) -> list:
        try:
            iframe_path = "/html/frameset/frameset/frame[1]"

            self.driver.get("http://results.jntuh.ac.in")
            iframe = self.driver.find_element_by_xpath(iframe_path)
            self.driver.switch_to.frame(iframe)

            body_xpath = "/html/body"
            body = self.driver.find_element_by_xpath(body_xpath)
            body = body.get_attribute('innerHTML')
            soup = BeautifulSoup(body, 'html.parser')
            notifications = []
            for each in soup.findAll("h3"):
                current = each.getText()
                date, description = current.split(" ", 1)
                date = date.lstrip("*(").rstrip(")")
                description = description.strip()
                if not "b.tech" in description.lower():
                    continue
                notifications.append({
                    "notification_date": date,
                    "notification_description": description
                })
            self.save_notifications(notifications)

        except Exception as e:
            self.logger.exception(e)
            with open("notifications.json", "r") as f:
                notifications = json.loads(f.read())
        if not notifications:
            self.logger.exception(
                "Something went wrong with fetching data from JNTUH servers")
            with open("notifications.json", "r") as f:
                notifications = json.loads(f.read())

        return notifications

    def save_notifications(self, notifications) -> None:
        """ A method to save the notifications """
        with open("notifications.json", "w") as f:
            f.write(json.dumps(notifications, indent=2))

    def save_table(self) -> None:
        """ A method to save the table locally """

        table = self.get_table_attribute()
        with open("table.html", "w") as f:
            f.write(table.get_attribute("innerHTML"))

    def save_exams_json(self, exams: dict) -> None:
        """ A method to save exams json object """

        with open('result-links.json', 'w') as f:
            f.write(json.dumps(exams, indent=2))

    def get_all_results(self) -> list:
        """ within the tablebody, there are table rows each row has two table-data elements
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
            self.logger.exception(f"Exception: {e}")
            # Reading the static html that has been saved locally
            soup = BeautifulSoup(open("table.html", "r"), 'html.parser')

        rows = soup.find_all("tr")
        regular_exams = []
        supply_exams = []
        unordered_results = []
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

            result_object = {
                "exam_name": exam_desc,
                "release_date": exam_date,
                "links": links,
            }
            for each_param in params:
                key, value = each_param.split("=")
                result_object[key] = value

            unordered_results.append(result_object)

            if "Regular" in exam_desc:
                result_object["id"] = regular_id
                regular_id += 1
                regular_exams.append(result_object)
            else:
                result_object["id"] = supply_id
                supply_id += 1
                supply_exams.append(result_object)

        all_exams = {
            "total-exam-result-releases": i,
            "total-regular-exam-result-releases": regular_id,
            "total-supply-exam-result-releases": supply_id,
            "regular": regular_exams,
            "supply": supply_exams,
        }

        self.save_exams_json(all_exams)

        return [all_exams, regular_exams, supply_exams, unordered_results]
