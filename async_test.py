import asyncio
from utils.constants import codes
from controllers.r18_all_results_service import get_r18_async_results


async def helper(hallticket, code):
    result = get_r18_async_results(hallticket.upper(), code)
    return result

async def main(hallticket):     
    print("WORKING")
    tasks = []
    for code in codes:
      tasks.append(asyncio.create_task(helper(hallticket, code)))

    responses = await asyncio.gather(*tasks)

    return responses



def get_all(hallticket):
    return asyncio.run(main(hallticket))
