# import http.client
# import logging
import aiohttp
# import urllib
import asyncio
import time
from bs4 import BeautifulSoup
# import requests

def get_student_info(sel_soup) -> dict:
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

def get_results_info(sel_soup):
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

results = []

# f"https://results-restapi.herokuapp.com/api/calculate?hallticket=185u1a05{i}&dob=3&degree=btech&examCode=1502&etype=r17", ssl=False


def get_tasks(session):
    tasks = []
    link = "http://results.jntuh.ac.in/results/resultAction?degree=btech"
    examCode = "&examCode=1502"
    etype = "&etype=r17"
    type = "&type=intgrade"
    result = "&result=null"
    grad = "&grad=null"
    for i in range(60, 99):
        htno = f"&htno=185U1A05{i}"
        print(f"185u1a0{i}")
        tasks.append(asyncio.create_task(session.get(link + examCode + etype + type + result + grad + htno)))
    return tasks


start = time.time()


async def get_result():
    responses = []
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks(session)
        responses = await asyncio.gather(*tasks)
        for resp in responses:
            html = await resp.text()
            results.append(html)

    return responses


responses = asyncio.run(get_result())
all_results = []
for each in results:
    sel_soup = BeautifulSoup(each, 'html.parser')
    try:
        student = get_student_info(sel_soup)
        results = get_results_info(sel_soup)
        all_results.append([student, results])
    except Exception as e:
        print(e)
        print(each)


print(all_results)
print(len(all_results))
end = time.time()
print(end-start)


# start = time.time()
# for i in range(60, 65):
# print("sending request", i)
# # requests.get(
# # "https://results-restapi.herokuapp.com/api/calculate?hallticket=185u1a0561&dob=3&degree=btech&examCode=1502&etype=r17")
# requests.get("https://randomuser.me/api", headers={"Connection": "close"})
# print("DONE", i)
# end = time.time()
# print(end - start)


# def sessionsway():
#     session = requests.Session()

#     start = time.time()
#     for i in range(60, 100):
#         print("getting ", i)
#         session.get(
#             f'http://results-restapi.herokuapp.com/api/calculate?hallticket=185u1a05{i}&dob=3&degree=btech&examCode=1502&etype=r17')
#         # session.get("https://randomuser.me/api")
#         print("done ", i)
#     end = time.time()

#     print(end - start)
