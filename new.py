# import http.client
# import logging
from datetime import timedelta
import aiohttp
import json
# import urllib
import asyncio
import time
from bs4 import BeautifulSoup
import redis

grades = {
    "O": 10,
    "A+": 9,
    "A": 8,
    "B+": 7,
    "B": 6,
    "C": 5,
    "F": 0,
    "Ab": 0,
}

def calculate_sgpa(results_object):
    sgpa = 0
    total_credits = 0
    for subject in results_object[1]:
        total_credits += float(subject["subject_credits"])
        if subject["grade_earned"] == "F" or subject["grade_earned"] == "-":
            sgpa = 0
            break
        if not subject["grade_earned"] in grades.keys():
            sgpa = 0
            break
        sgpa += grades[subject["grade_earned"]] * float(subject["subject_credits"])

    if total_credits == 0:
        sgpa = 0
    else:
        sgpa = round(sgpa / total_credits, 2)
    results_object.insert(0, {"SGPA": sgpa if sgpa else "FAIL"})

    return results_object

def get_hallticket_helper(roll_number, i):
    if i < 10:
        hallticket = roll_number + "0" + str(i)
    elif i < 100:
        hallticket = roll_number + str(i)
    elif i > 99 and i < 110:
        hallticket = roll_number + "A" + str(i - 100)
    elif i > 109 and i < 120:
        hallticket = roll_number + "B" + str(i - 110)
    elif i > 119 and i < 130:
        hallticket = roll_number + "C" + str(i - 120)
    elif i > 129 and i < 140:
        hallticket = roll_number + "D" + str(i - 130)
    elif i > 139 and i < 150:
        hallticket = roll_number + "E" + str(i - 140)
    elif i > 149 and i < 160:
        hallticket = roll_number + "F" + str(i - 150)
    elif i > 159 and i < 170:
        hallticket = roll_number + "G" + str(i - 160)
    elif i > 169 and i < 180:
        hallticket = roll_number + "H" + str(i - 170)
    elif i > 179 and i < 190:
        hallticket = roll_number + "J" + str(i - 180)
    elif i > 189 and i < 200:
        hallticket = roll_number + "K" + str(i - 190)
    elif i > 199 and i < 210:
        hallticket = roll_number + "L" + str(i - 200)
    elif i > 209 and i < 220:
        hallticket = roll_number + "M" + str(i - 210)
    elif i > 219 and i < 230:
        hallticket = roll_number + "N" + str(i - 220)
    elif i > 229 and i < 240:
        hallticket = roll_number + "P" + str(i - 230)

    return hallticket
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


# f"https://results-restapi.herokuapp.com/api/calculate?hallticket=185u1a05{i}&dob=3&degree=btech&examCode=1502&etype=r17", ssl=False


async def create(session, examCode, etype, type, result, htno, redis_client):
    # Check if the given specific hallticket along with other details are already cached in redis
    current_key = f"calculate-{htno}-'btech'-{examCode}-{etype}-{type}-{result}"
    redis_response = redis_client.get(current_key)

    if redis_response != None:
        redis_out = json.loads(redis_response)
        return redis_out

    # Else, do some async stuff
    try:
        link = "http://results.jntuh.ac.in/results/resultAction?degree=btech"
        resp = await session.get(link + examCode + etype + type + result + "&grad=null" + f"&htno={htno}")
        print(link + examCode + etype + type + result + "&grad=null" + f"&htno={htno}")
        if resp.status == 500:
            raise Exception("First link failed to get details")
        html =  await resp.text()
        try:
            sel_soup = BeautifulSoup(html, 'html.parser')
            student = get_student_info(sel_soup)
            results = get_results_info(sel_soup)

            new_result = calculate_sgpa([student, results])
            # Now, cache it with the current_key in the redis client and the return

            redis_client.set(current_key, json.dumps(new_result))
            redis_client.expire(current_key, timedelta(minutes=30))

            return new_result
        except Exception as e:
            print("INSIDE SOUP: ",e)
            redis_client.set(current_key, json.dumps({htno: "FALSE"}))
            redis_client.expire(current_key, timedelta(minutes=30))

    except Exception as e:
        try:
            link = 'http://202.63.105.184/results/resultAction?degree=btech'
            resp = await session.get(link + examCode + etype + type + result + "&grad=null" + f"&hallticket={htno}")
            print(link + examCode + etype + type + result + "&grad=null" + f"&htno={htno}")
            if resp.status == 500:
                raise Exception("Second link also failed to get details")
            html = await resp.text()
            try:
                sel_soup = BeautifulSoup(html, 'html.parser')
                student = get_student_info(sel_soup)
                results = get_results_info(sel_soup)

                new_result = calculate_sgpa([student, results])
                # Now, cache it with the current_key in the redis client and the return

                redis_client.set(current_key, json.dumps(new_result))
                redis_client.expire(current_key, timedelta(minutes=30))
            except Exception as e:
                print("INSIDE SOUP",e)
                redis_client.set(current_key, json.dumps({htno: "FALSE"}))
                redis_client.expire(current_key, timedelta(minutes=30))
        except Exception as e:
            print("BOTH THE LINKS FAILED TO GET RESULT: ",e)


def get_tasks(session, examCode, etype, type, result, roll_number, start, end, redis_client):
    tasks = []
    for i in range(start, end+1):
        htno = get_hallticket_helper(roll_number, i)
        print(htno)
        # print(f"185u1a0{i}")
        tasks.append(asyncio.create_task(create(session, examCode , etype , type , result ,  htno, redis_client=redis_client)))

    return tasks



async def get_result(roll_number, start, end, examCode, etype, type, result, redis_client):
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks(session, examCode, etype, type, result, roll_number, start, end, redis_client)
        responses = await asyncio.gather(*tasks)
        for result in responses:
            if result:
                results.append(result)

    return results


def get_results_async(hallticket_from, hallticket_to, examCode, etype, type, result, redis_client):

    string_dict = {
        "A": 0,
        "B": 1,
        "C": 2,
        "D": 3,
        "E": 4,
        "F": 5,
        "G": 6,
        "H": 7,
        "J": 8,
        "K": 9,
        "L": 10,
        "M": 11,
        "N": 12,
        "P": 13,
    }

    roll_number = hallticket_from[0:8]
    s1 = str(hallticket_from[8:10])
    s2 = str(hallticket_to[8:10])

    def test(s1):
        try:
            s1 = int(s1)
            return s1
        except:
            s1 = str(string_dict[s1[0]]) + str(s1[1])
            s1 = 100 + int(s1)
        return s1

    start = test(s1)
    end = test(s2)

    redis_client = redis.Redis(host="localhost", port=6379, db=0)
    results = asyncio.run(get_result(roll_number, start, end, f"&examCode={examCode}", f"&etype={etype}", f"&type={type}", f"&result={result}", redis_client))

    if results.count(None): results.remove(None)
    # print(json.dumps(results, indent=2))
    # print(len(results))


    return results
