from datetime import timedelta
import json
import os
import platform
import threading

from flask import Flask, Response, request, render_template
import redis
from selenium import webdriver

from controllers.all_results_service import AllResults
from controllers.r18_all_results_service import get_r18_async_results
from controllers.service import Service
from controllers.async_service import get_results_async
from utils.utils import calculate_sgpa, get_hallticket_helper


def init_firefox_driver():
    firefox_options = webdriver.FirefoxOptions()
    driver_file = (
        "drivers/geckodriver"
        if platform.system() == "Linux"
        else "drivers/geckodriver.exe"
    )
    # Arguments for Firefox driver
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")

    # Firefox Driver
    driver = webdriver.Firefox(
        executable_path=os.path.join(os.getcwd(), driver_file), options=firefox_options
    )

    return driver


def init_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    # Specifying the driver options for chrome
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    # Starting the driver
    driver = webdriver.Chrome(
        executable_path=os.environ.get("CHROMEDRIVER_PATH"),
        chrome_options=chrome_options,
    )

    return driver


# TODO: Swap the drivers and redis client
# driver = init_firefox_driver()
# redis_client = redis.Redis(host="localhost", port=6379, db=0)
driver = init_chrome_driver()
redis_client = redis.from_url(os.environ.get("REDIS_URL"))

# Initializing the Crawler object from service
# Injecting the driver dependency
old_scrapper = Service(driver)
new_scrapper = AllResults(driver)


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/all-r18/<hallticket>")
def fetch_all_r18_results(hallticket):
    current_key = f"r18-{hallticket}"

    redis_response = redis_client.get(current_key)
    if redis_response != None:
        data = json.loads(redis_response)
        return Response(json.dumps(data), mimetype="application/json")
    results = {}
    all_results = []
    from utils.constants import codes

    try:
        for code in codes:
            result = get_r18_async_results(hallticket.upper(), code)
            if not results:
                results["details"] = result["student_details"]
            new = {
                key: value
                for key, value in result.items()
                if key != "student_details" and value
            }
            if new:
                all_results.append(new)
    except Exception as e:
        print(e)
        return Response(json.dumps({"error": "something went wrong with server"}))
    results["results"] = all_results
    total_gpa = 0
    for year in results["results"]:
        if len(year) < 2:
            total_gpa = 0
            break
        total_gpa += float(year["SGPA"])
    if total_gpa:
        total_gpa /= len(results["results"])
        results["overall_gpa"] = total_gpa

    redis_client.set(current_key, json.dumps({"data": results}))
    redis_client.expire(current_key, timedelta(hours=1))
    return Response(json.dumps({"data": results}), mimetype="application/json")


@app.route("/<hallticket>/<dob>/<year>", methods=["GET"])
def routing_path(hallticket, dob, year):
    current_key = f"{hallticket}-{year}"

    redis_response = redis_client.get(current_key)
    if redis_response != None:
        result = json.loads(redis_response)
    else:
        result = old_scrapper.get_result(hallticket, dob, year)
        if "error" in result:
            return Response(json.dumps(result), mimetype="application/json", status=503)
        redis_client.set(current_key, json.dumps(result))
        redis_client.expire(current_key, timedelta(minutes=30))

    return Response(json.dumps(result), mimetype="application/json")


@app.route("/calculate/<hallticket>/<dob>/<year>", methods=["GET"])
def calculate(hallticket, dob, year):
    current_key = f"calculate-{hallticket}-{year}"

    redis_response = redis_client.get(current_key)
    if redis_response != None:
        result = json.loads(redis_response)
    else:
        result = old_scrapper.get_result(hallticket, dob, year)
        if "error" in result:
            return Response(json.dumps(result), mimetype="application/json", status=503)
        result = calculate_sgpa(result)
        redis_client.set(current_key, json.dumps(result))
        redis_client.expire(current_key, timedelta(minutes=30))

    return Response(json.dumps(result), mimetype="application/json")


@app.route("/result", methods=["GET"])
def request_param_path():

    hallticket = request.args.get("hallticket")
    dob = request.args.get("dob")
    year = request.args.get("year")

    current_key = f"result-{hallticket}-{year}"
    redis_response = redis_client.get(current_key)
    if redis_response != None:
        result = json.loads(redis_response)
    else:
        result = old_scrapper.get_result(hallticket, dob, year)
        if "error" in result:
            return Response(json.dumps(result), mimetype="application/json", status=503)
        redis_client.set(current_key, json.dumps(result))
        redis_client.expire(current_key, timedelta(minutes=30))

    return Response(json.dumps(result), mimetype="application/json")


@app.route("/new/all", methods=["GET"])
def all_results():
    current_key = "all_exams"

    redis_response = redis_client.get(current_key)
    if redis_response != None:
        all_exams = json.loads(redis_response)
    else:
        all_exams, _, _, _ = new_scrapper.get_all_results()
        redis_client.set(current_key, json.dumps(all_exams))
        redis_client.expire(current_key, timedelta(minutes=30))

    return Response(json.dumps(all_exams), mimetype="application/json")


@app.route("/new/all/regular", methods=["GET"])
def all_regular():
    current_key = "all_regular"
    refresh = request.args.get("refresh")
    if refresh is not None:
        refresh = True

    redis_response = redis_client.get(current_key)
    if redis_response != None and not refresh:
        regular_exams = json.loads(redis_response)
    else:
        _, regular_exams, _, _ = new_scrapper.get_all_results()
        redis_client.set(current_key, json.dumps(regular_exams))
        redis_client.expire(current_key, timedelta(minutes=30))

    return Response(json.dumps(regular_exams), mimetype="application/json")


@app.route("/new/all/supply", methods=["GET"])
def all_supply():
    current_key = "all_supply"
    refresh = request.args.get("refresh")
    if refresh is not None:
        refresh = True
    redis_response = redis_client.get(current_key)
    if redis_response != None and not refresh:
        supply_exams = json.loads(redis_response)
    else:
        _, _, supply_exams, _ = new_scrapper.get_all_results()
        redis_client.set(current_key, json.dumps(supply_exams))
        redis_client.expire(current_key, timedelta(minutes=30))

    return Response(json.dumps(supply_exams), mimetype="application/json")


@app.route("/api", methods=["GET"])
def get_specific_result():
    hallticket = request.args.get("hallticket")
    dob = request.args.get("dob")
    degree = request.args.get("degree")
    examCode = request.args.get("examCode")
    etype = request.args.get("etype")
    type = request.args.get("type")
    result = request.args.get("result") or ""
    print(hallticket, dob, degree, examCode, etype, type, result)

    current_key = f"{hallticket}-{degree}-{examCode}-{etype}-{type}-{result}"

    redis_response = redis_client.get(current_key)
    if redis_response != None:
        resp = json.loads(redis_response)
    else:
        resp = old_scrapper.get_result_with_url(
            hallticket, dob, degree, examCode, etype, type, result
        )
        if "error" in resp:
            return Response(json.dumps(resp), mimetype="application/json", status=503)
        redis_client.set(current_key, json.dumps(resp))
        redis_client.expire(current_key, timedelta(minutes=30))

    return Response(json.dumps(resp), mimetype="application/json")


@app.route("/api/calculate", methods=["GET"])
def get_specific_result_with_sgpa():
    hallticket = request.args.get("hallticket")
    dob = request.args.get("dob")
    degree = request.args.get("degree")
    examCode = request.args.get("examCode")
    etype = request.args.get("etype")
    type = request.args.get("type")
    result = request.args.get("result") or ""

    current_key = f"calculate-{hallticket}-{degree}-{examCode}-{etype}-{type}-{result}"
    redis_response = redis_client.get(current_key)
    if redis_response != None:
        result = json.loads(redis_response)
    else:
        resp = old_scrapper.get_result_with_url(
            hallticket, dob, degree, examCode, etype, type, result
        )
        if "error" in resp:
            return Response(json.dumps(resp), mimetype="application/json", status=503)
        result = calculate_sgpa(resp)
        redis_client.set(current_key, json.dumps(result))
        redis_client.expire(current_key, timedelta(minutes=30))

    return Response(json.dumps(result), mimetype="application/json")


@app.route("/api/bulk/calculate", methods=["GET"])
def get_bulk_results():

    from utils.constants import string_dict

    hallticket_from = request.args.get("hallticket_from").upper()
    hallticket_to = request.args.get("hallticket_to").upper()
    degree = request.args.get("degree")
    examCode = request.args.get("examCode")
    etype = request.args.get("etype")
    type = request.args.get("type")
    result = request.args.get("result") or "null"
    # hallticket = hallticket_from[:-2]

    if hallticket_from[0:8] != hallticket_to[0:8]:
        return Exception("Starting and ending hallticket should be same")

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

    if end - start < 0 or end - start > 210:
        return Exception("SOMETHING WENT WRONG")

    redis_response = redis_client.get(
        hallticket_from + hallticket_to + examCode + etype + type
    )
    if redis_response != None:
        return Response(redis_response, mimetype="application/json")

    # Check if all the halltickets are already cached, if so, return them.
    results = []
    for i in range(start, end + 1):

        hallticket = get_hallticket_helper(roll_number, i)
        current_key = (
            f"calculate-{hallticket}-{degree}-{examCode}-{etype}-{type}-{result}"
        )
        redis_response = redis_client.get(current_key)

        if redis_response != None:
            redis_out = json.loads(redis_response)
            results.append(redis_out)
        else:
            break
    else:
        print("DIDN'T CREATE A NEW KEY, GOT RESULTS FROM HALLTICKETS CACHED")
        return Response(json.dumps(results), mimetype="application/json")

    redis_client.set(
        hallticket_from + hallticket_to + examCode + etype + type,
        json.dumps({"result": "loading"}),
    )
    redis_client.expire(
        hallticket_from + hallticket_to + examCode, timedelta(minutes=10)
    )

    def worker(hallticket_from, hallticket_to):
        print("WORKER IS RUNNING")
        results = get_results_async(
            hallticket_from, hallticket_to, examCode, etype, type, result, redis_client
        )

        redis_client.set(
            hallticket_from + hallticket_to + examCode + etype + type,
            json.dumps(results),
        )
        redis_client.expire(
            hallticket_from + hallticket_to + examCode + etype + type,
            timedelta(minutes=10),
        )

    threading.Thread(target=worker, args=(hallticket_from, hallticket_to)).start()

    # This is only going to return in the first call.
    return Response(
        redis_client.get(hallticket_from + hallticket_to + examCode + etype + type),
        mimetype="application/json",
    )


@app.route("/new/", methods=["GET"])
def all_unordered_results():
    _, _, _, unordered_results = new_scrapper.get_all_results()
    return Response(json.dumps(unordered_results), mimetype="application/json")


@app.route("/notifications", methods=["GET"])
def notifications():
    refresh = request.args.get("refresh")
    if refresh is not None:
        refresh = True
    current_key = "notifications"

    redis_response = redis_client.get(current_key)
    if redis_response != None and not refresh:
        result = json.loads(redis_response)
    else:
        result = new_scrapper.get_notifiations()
        redis_client.set(current_key, json.dumps(result))
        redis_client.expire(current_key, timedelta(minutes=30))

    return Response(json.dumps(result), mimetype="application/json")


if __name__ == "__main__":

    app.run()
