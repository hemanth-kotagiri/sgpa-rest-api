import asyncio
import aiohttp
from bs4 import BeautifulSoup
from utils.constants import payloads, grades, headers
from utils.utils import exam_codes, get_student_info, invalid_hallticket


class Results:
    def __init__(self):
        self.data = {}
        self.data.clear()
        self.tasks = []

    def get_tasks(self, session, codes, roll):
        url = "http://results.jntuh.ac.in/resultAction"
        for payload in payloads:
            for code in codes:
                payload_data = "degree=btech&examCode=" + str(code) + payload + roll
                self.tasks.append(
                    session.post(url, data=payload_data, headers=headers, ssl=False)
                )
        return self.tasks

    def grade_calculate(self, value):
        try:
            total, cr = 0, 0
            for data in value:
                if "student_details" in data:
                    pass
                else:
                    if (
                        value[data]["grade_earned"] == "F"
                        or value[data]["grade_earned"] == "Ab"
                    ):
                        return ""
                    total = total + int(grades[value[data]["grade_earned"]]) * float(
                        value[data]["subject_credits"]
                    )
                    cr = cr + float(value[data]["subject_credits"])
            self.data["SGPA"] = "{0:.2f}".format(round(total / cr, 2))
        except:
            pass

    def worker(self, code, soup):
        if invalid_hallticket(soup):
            print("INVALID HALLTICKET")
            return []
        try:
            table = soup.find_all("table")
            table2 = table[1].find_all("tr")
            table2 = table2[1:]

            for row in table2:
                bTags = row.find_all("b")
                if not bTags[0].text.isalnum():
                    continue
                current_subject = []
                count = 1

                for b in bTags:
                    if count <= 7:
                        current_subject.append(b.text)
                        count += 1

                if not current_subject:
                    continue
                try:
                    if (
                        self.data[code][current_subject[0]]["grade_earned"] != "F"
                        and self.data[code][current_subject[0]]["grade_earned"] != "Ab"
                    ):
                        continue
                except Exception as e:
                    print("EXCEPTION: ", e)
                subject_code = current_subject[0]
                if current_subject:
                    self.data[code][subject_code] = {}
                    self.data[code][subject_code]["subject_code"] = current_subject[0]
                    self.data[code][subject_code]["subject_name"] = current_subject[1]
                    self.data[code][subject_code]["internal_marks"] = current_subject[2]
                    self.data[code][subject_code]["external_marks"] = current_subject[3]
                    self.data[code][subject_code]["total_marks"] = current_subject[4]
                    self.data[code][subject_code]["grade_earned"] = current_subject[5]
                    self.data[code][subject_code]["subject_credits"] = current_subject[
                        6
                    ]

            self.data["student_details"] = get_student_info(soup)
        except:
            pass

    async def get_results(self, code, roll):
        codes = exam_codes(code)
        async with aiohttp.ClientSession() as session:
            tasks = self.get_tasks(session, codes, roll)
            responses = await asyncio.gather(*tasks)
            self.data[code] = {}
            for response in responses:
                r = await response.text()
                soup = BeautifulSoup(r, "html.parser")
                self.worker(code, soup)

        self.grade_calculate(self.data[code])

        return self.data


# Function called from views
def get_r18_async_results(roll, code):
    worker_obj = Results()
    result = asyncio.run(worker_obj.get_results(code, roll))
    del worker_obj
    return result
