from bs4 import BeautifulSoup
import asyncio
import aiohttp
from aiohttp.client import ClientTimeout
from utils.utils import calculate_sgpa
from utils.utils import get_results_info, get_student_info

# TODO: Create a common metaclass/abstractclass using ABC to have similar async jobs


# TODO: Move this to utils and don't use match
def exam_codes(code):

    arr11 = ["1323", "1358", "1404", "1430", "1467", "1504"]
    arr12 = ["1356", "1381", "1435", "1448", "1481", "1503"]
    arr21 = ["1391", "1425", "1449", "1496", "1560"]
    arr22 = ["1437", "1447", "1476", "1501", "1565"]
    arr31 = ["1454", "1491", "1550"]
    arr32 = ["1502", "1555"]
    arr41 = ["1545"]
    arr42 = ["1580"]

    match code:
        case "1-1":
            return arr11
        case "1-2":
            return arr12
        case "2-1":
            return arr21
        case "2-2":
            return arr22
        case "3-1":
            return arr31
        case "3-2":
            return arr32
        case "4-1":
            return arr41
        case "4-2":
            return arr42
        case default:
            return []


# TODO: Move this to utils
def invalid_hallticket(sel_soup):
    if sel_soup.find_all(
        lambda tag: tag.name == "div" and "invalid hallticket number" in tag.text
    ):
        return True
    return False


async def create(session, hallticket, code, redis_client):
    # Else, do some async stuff
    try:
        link = "http://results.jntuh.ac.in/results/resultAction?degree=btech"
        resp = await session.get(
            link
            + f"&examCode={code}"
            + "&etype=r17"
            + "&type=intgrade"
            + "&result=null"
            + "&grad=null"
            + f"&htno={hallticket}",
            timeout=ClientTimeout(total=5.0),
        )
        if resp.status == 500:
            raise Exception("First link failed to get details")
        html = await resp.text()
        try:
            sel_soup = BeautifulSoup(html, "html.parser")
            if invalid_hallticket(sel_soup):
                return None
            student = get_student_info(sel_soup)
            results = get_results_info(sel_soup)

            new_result = calculate_sgpa([student, results])
            # Now, cache it with the current_key in the redis client and the return

            # redis_client.set(current_key, json.dumps(new_result))
            # redis_client.expire(current_key, timedelta(minutes=30))

            return new_result
        except Exception as e:
            print("INSIDE SOUP: ", e)
            # redis_client.set(current_key, json.dumps({htno: "FALSE"}))
            # redis_client.expire(current_key, timedelta(minutes=30))

    # TODO
    except Exception as e:
        print(e)
        # try:
        #     link = "http://202.63.105.184/results/resultAction?degree=btech"
        #     resp = await session.get(
        #         link
        #         + examCode
        #         + etype
        #         + type
        #         + result
        #         + "&grad=null"
        #         + f"&hallticket={htno}",
        #         timeout=ClientTimeout(total=5.0),
        #     )
        #     print(
        #         link + examCode + etype + type + result + "&grad=null" + f"&htno={htno}"
        #     )
        #     if resp.status == 500:
        #         raise Exception("Second link also failed to get details")
        #     html = await resp.text()
        #     try:
        #         sel_soup = BeautifulSoup(html, "html.parser")
        #         student = get_student_info(sel_soup)
        #         results = get_results_info(sel_soup)
        #
        #         new_result = calculate_sgpa([student, results])
        #         # Now, cache it with the current_key in the redis client and the return
        #
        #         # redis_client.set(current_key, json.dumps(new_result))
        #         # redis_client.expire(current_key, timedelta(minutes=30))
        #
        #         return new_result
        #     except Exception as e:
        #         print("INSIDE SOUP", e)
        #         # redis_client.set(current_key, json.dumps({htno: "FALSE"}))
        #         # redis_client.expire(current_key, timedelta(minutes=30))
        # except Exception as e:
        #     print("BOTH THE LINKS FAILED TO GET RESULT: ", e)
        #     # redis_client.set(current_key, json.dumps({htno: "FALSE"}))
        #     # redis_client.expire(current_key, timedelta(minutes=30))


def get_tasks(session, hallticket, codes, redis_client):
    tasks = []
    for code in codes:
        tasks.append(
            asyncio.create_task(
                create(session, hallticket, code, redis_client=redis_client)
            )
        )

    return tasks


async def get_result(hallticket, exam, redis_client):
    results = []
    codes = exam_codes(exam)
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks(session, hallticket, codes, redis_client)
        responses = await asyncio.gather(*tasks)
        for result in responses:
            if result:
                results.append(result)
    return results


# TODO: more than one exam -> Remove exam dependency
def get_r18_results_async(hallticket, exam, redis_client):

    results = asyncio.run(
        get_result(
            hallticket,
            exam,
            redis_client,
        )
    )

    if results.count(None):
        results.remove(None)

    return results
