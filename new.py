# import http.client
# import logging
import aiohttp
# import urllib
import asyncio
import time
import requests


results = []

# f"https://results-restapi.herokuapp.com/api/calculate?hallticket=185u1a05{i}&dob=3&degree=btech&examCode=1502&etype=r17", ssl=False


def get_tasks(session):
    tasks = []
    for i in range(60, 100):
        print(f"185u1a0{i}")
        tasks.append(asyncio.create_task(session.get(
            f"http://results-restapi.herokuapp.com/api/calculate?hallticket=185u1a05{i}&dob=3&degree=btech&examCode=1502&etype=r17", ssl=False)))
    return tasks


start = time.time()


async def get_result():
    responses = []
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks(session)
        responses = await asyncio.gather(*tasks)
        for resp in responses:
            results.append(resp)

    return responses


responses = asyncio.run(get_result())
print(len(responses))

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


def sessionsway():
    session = requests.Session()

    start = time.time()
    for i in range(60, 100):
        print("getting ", i)
        session.get(
            f'http://results-restapi.herokuapp.com/api/calculate?hallticket=185u1a05{i}&dob=3&degree=btech&examCode=1502&etype=r17')
        # session.get("https://randomuser.me/api")
        print("done ", i)
    end = time.time()

    print(end - start)
