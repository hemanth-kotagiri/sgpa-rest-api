from datetime import timedelta
import aiohttp
import json

import asyncio
from bs4 import BeautifulSoup
from utils.utils import get_hallticket_helper, calculate_sgpa
from utils.utils import get_results_info, get_student_info


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
        resp = await session.get(
            link + examCode + etype + type + result + "&grad=null" + f"&htno={htno}",
            timeout=2,
        )
        print(link + examCode + etype + type + result + "&grad=null" + f"&htno={htno}")
        if resp.status == 500:
            raise Exception("First link failed to get details")
        html = await resp.text()
        try:
            sel_soup = BeautifulSoup(html, "html.parser")
            student = get_student_info(sel_soup)
            results = get_results_info(sel_soup)

            new_result = calculate_sgpa([student, results])
            # Now, cache it with the current_key in the redis client and the return

            redis_client.set(current_key, json.dumps(new_result))
            redis_client.expire(current_key, timedelta(minutes=30))

            return new_result
        except Exception as e:
            print("INSIDE SOUP: ", e)
            redis_client.set(current_key, json.dumps({htno: "FALSE"}))
            redis_client.expire(current_key, timedelta(minutes=30))

    except Exception as e:
        try:
            link = "http://202.63.105.184/results/resultAction?degree=btech"
            resp = await session.get(
                link
                + examCode
                + etype
                + type
                + result
                + "&grad=null"
                + f"&hallticket={htno}",
                timeout=2,
            )
            print(
                link + examCode + etype + type + result + "&grad=null" + f"&htno={htno}"
            )
            if resp.status == 500:
                raise Exception("Second link also failed to get details")
            html = await resp.text()
            try:
                sel_soup = BeautifulSoup(html, "html.parser")
                student = get_student_info(sel_soup)
                results = get_results_info(sel_soup)

                new_result = calculate_sgpa([student, results])
                # Now, cache it with the current_key in the redis client and the return

                redis_client.set(current_key, json.dumps(new_result))
                redis_client.expire(current_key, timedelta(minutes=30))

                return new_result
            except Exception as e:
                print("INSIDE SOUP", e)
                redis_client.set(current_key, json.dumps({htno: "FALSE"}))
                redis_client.expire(current_key, timedelta(minutes=30))
        except Exception as e:
            print("BOTH THE LINKS FAILED TO GET RESULT: ", e)
            redis_client.set(current_key, json.dumps({htno: "FALSE"}))
            redis_client.expire(current_key, timedelta(minutes=30))


def get_tasks(
    session, examCode, etype, type, result, roll_number, start, end, redis_client
):
    tasks = []
    for i in range(start, end + 1):
        htno = get_hallticket_helper(roll_number, i)
        print(htno)
        tasks.append(
            asyncio.create_task(
                create(
                    session,
                    examCode,
                    etype,
                    type,
                    result,
                    htno,
                    redis_client=redis_client,
                )
            )
        )

    return tasks


async def get_result(
    roll_number, start, end, examCode, etype, type, result, redis_client
):
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks(
            session,
            examCode,
            etype,
            type,
            result,
            roll_number,
            start,
            end,
            redis_client,
        )
        responses = await asyncio.gather(*tasks)
        for result in responses:
            if result:
                results.append(result)

    return results


def get_results_async(
    hallticket_from, hallticket_to, examCode, etype, type, result, redis_client
):

    from utils.constants import string_dict

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

    results = asyncio.run(
        get_result(
            roll_number,
            start,
            end,
            f"&examCode={examCode}",
            f"&etype={etype}",
            f"&type={type}",
            f"&result={result}",
            redis_client,
        )
    )

    if results.count(None):
        results.remove(None)

    return results
