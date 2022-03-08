from datetime import timedelta
import json
import os
import platform
import threading

from flask import Flask, Response, request, render_template
import redis
from selenium import webdriver

from controllers.all_results_service import AllResults
from controllers.service import Service


def init_firefox_driver():
    firefox_options = webdriver.FirefoxOptions()
    driver_file = "drivers/geckodriver" if platform.system() == "Linux" else "drivers/geckodriver.exe"
    # Arguments for Firefox driver
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")

    # Firefox Driver
    driver = webdriver.Firefox(
        executable_path=os.path.join(os.getcwd(), driver_file), options=firefox_options)

    return driver


def init_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    # Specifying the driver options for chrome
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = os.environ.get(
        "GOOGLE_CHROME_BIN")
    # Starting the driver
    driver = webdriver.Chrome(
        executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

    return driver


# driver = init_firefox_driver()
# redis_client = redis.Redis(host="localhost", port=6379, db=0)
driver = init_chrome_driver()
redis_client = redis.from_url(os.environ.get("REDIS_URL"))

# Initializing the Crawler object from service
# Injecting the driver dependency
old_scrapper = Service(driver)
new_scrapper = AllResults(driver)

grades = {
    "O":  10,
    "A+": 9,
    "A":  8,
    "B+": 7,
    "B":  6,
    "C":  5,
    "F":  0,
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
        sgpa += grades[subject["grade_earned"]] * \
            float(subject["subject_credits"])

    if total_credits == 0: sgpa = 0
    else: sgpa = round(sgpa/total_credits, 2)
    results_object.insert(0, {"SGPA": sgpa if sgpa else "FAIL"})

    return results_object


app = Flask(__name__)


@app.route("/")
def index():

    return render_template("index.html")


@app.route("/<hallticket>/<dob>/<year>", methods=["GET"])
def routing_path(hallticket, dob, year):
    current_key = f"{hallticket}-{year}"

    redis_response = redis_client.get(current_key)
    if redis_response != None:
        result = json.loads(redis_response)
    else:
        result = old_scrapper.get_result(hallticket, dob, year)
        if "error" in result:
            return Response(json.dumps(result),  mimetype='application/json', status=503)
        redis_client.set(current_key, json.dumps(result))
        redis_client.expire(current_key, timedelta(minutes=30))

    return Response(json.dumps(result),  mimetype='application/json')


@app.route("/calculate/<hallticket>/<dob>/<year>", methods=["GET"])
def calculate(hallticket, dob, year):
    current_key = f"calculate-{hallticket}-{year}"

    redis_response = redis_client.get(current_key)
    if redis_response != None:
        result = json.loads(redis_response)
    else:
        result = old_scrapper.get_result(hallticket, dob, year)
        if "error" in result:
            return Response(json.dumps(result),  mimetype='application/json', status=503)
        result = calculate_sgpa(result)
        redis_client.set(current_key, json.dumps(result))
        redis_client.expire(current_key, timedelta(minutes=30))

    return Response(json.dumps(result),  mimetype='application/json')


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
            return Response(json.dumps(result),  mimetype='application/json', status=503)
        redis_client.set(current_key, json.dumps(result))
        redis_client.expire(current_key, timedelta(minutes=30))

    return Response(json.dumps(result),  mimetype='application/json')


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

    return Response(json.dumps(all_exams),  mimetype='application/json')


@app.route("/new/all/regular", methods=["GET"])
def all_regular():
    current_key = "all_regular"

    redis_response = redis_client.get(current_key)
    if redis_response != None:
        regular_exams = json.loads(redis_response)
    else:
        _, regular_exams, _, _ = new_scrapper.get_all_results()
        redis_client.set(current_key, json.dumps(regular_exams))
        redis_client.expire(current_key, timedelta(minutes=30))

    return Response(json.dumps(regular_exams),  mimetype='application/json')


@app.route("/new/all/supply", methods=["GET"])
def all_supply():
    current_key = "all_supply"
    redis_response = redis_client.get(current_key)
    if redis_response != None:
        supply_exams = json.loads(redis_response)
    else:
        _, _, supply_exams, _ = new_scrapper.get_all_results()
        redis_client.set(current_key, json.dumps(supply_exams))
        redis_client.expire(current_key, timedelta(minutes=30))

    return Response(json.dumps(supply_exams),  mimetype='application/json')


@app.route("/api", methods=["GET"])
def get_specific_result():
    hallticket = request.args.get("hallticket")
    dob = request.args.get("dob")
    degree = request.args.get("degree")
    examCode = request.args.get("examCode")
    etype = request.args.get("etype")
    type = request.args.get("type")
    result = request.args.get("result") or ''
    print(hallticket, dob, degree, examCode, etype, type, result)

    current_key = f"{hallticket}-{degree}-{examCode}-{etype}-{type}-{result}"

    redis_response = redis_client.get(current_key)
    if redis_response != None:
        resp = json.loads(redis_response)
    else:
        resp = old_scrapper.get_result_with_url(
            hallticket, dob, degree, examCode, etype, type, result)
        if "error" in resp:
            return Response(json.dumps(resp),  mimetype='application/json', status=503)
        redis_client.set(current_key, json.dumps(resp))
        redis_client.expire(current_key, timedelta(minutes=30))

    return Response(json.dumps(resp),  mimetype='application/json')


@app.route("/api/calculate", methods=["GET"])
def get_specific_result_with_sgpa():
    hallticket = request.args.get("hallticket")
    dob = request.args.get("dob")
    degree = request.args.get("degree")
    examCode = request.args.get("examCode")
    etype = request.args.get("etype")
    type = request.args.get("type")
    result = request.args.get("result") or ''

    current_key = f"calculate-{hallticket}-{degree}-{examCode}-{etype}-{type}-{result}"
    redis_response = redis_client.get(current_key)
    if redis_response != None:
        result = json.loads(redis_response)
    else:
        resp = old_scrapper.get_result_with_url(
            hallticket, dob, degree, examCode, etype, type, result)
        if "error" in resp:
            return Response(json.dumps(resp),  mimetype='application/json', status=503)
        result = calculate_sgpa(resp)
        redis_client.set(current_key, json.dumps(result))
        redis_client.expire(current_key, timedelta(minutes=30))

    return Response(json.dumps(result),  mimetype='application/json')


def get_hallticket_helper(roll_number, i):
    if (i < 10):
        hallticket = roll_number + '0' + str(i)
    elif (i < 100):
        hallticket = roll_number + str(i)
    elif i > 99 and i < 110:
        hallticket = roll_number + 'A' + str(i - 100)
    elif i > 109 and i < 120:
        hallticket = roll_number + 'B' + str(i - 110)
    elif i > 119 and i < 130:
        hallticket = roll_number + 'C' + str(i - 120)
    elif i > 129 and i < 140:
        hallticket = roll_number + 'D' + str(i - 130)
    elif i > 139 and i < 150:
        hallticket = roll_number + 'E' + str(i - 140)
    elif i > 149 and i < 160:
        hallticket = roll_number + 'F' + str(i - 150)
    elif i > 159 and i < 170:
        hallticket = roll_number + 'G' + str(i - 160)
    elif i > 169 and i < 180:
        hallticket = roll_number + 'H' + str(i - 170)
    elif i > 179 and i < 190:
        hallticket = roll_number + 'j' + str(i - 180)

    return hallticket

@app.route("/api/bulk/calculate", methods=["GET"])
def get_bulk_results():
    string_dict = {
        'A': 0,
         'B': 1,
         'C': 2,
         'D': 3,
         'E': 4,
         'F': 5,
         'G': 6,
         'H': 7,
         'J': 8,
    }
    hallticket_from = request.args.get("hallticket_from")
    hallticket_to = request.args.get("hallticket_to")
    dob = request.args.get("dob")
    degree = request.args.get("degree")
    examCode = request.args.get("examCode")
    etype = request.args.get("etype")
    type = request.args.get("type")
    result = request.args.get("result") or ''
    # hallticket = hallticket_from[:-2]

    if(hallticket_from[0:8] != hallticket_to[0:8]):
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

    if end-start < 0 or end-start > 210:
        return Exception("SOMETHING WENT WRONG")

    redis_response = redis_client.get(hallticket_from + hallticket_to + examCode)
    if redis_response != None:
        return Response(redis_response, mimetype='application/json')

    # Check if all the halltickets are already cached, if so, return them.
    results = []
    for i in range(start, end+1):

        hallticket = get_hallticket_helper(roll_number, i)
        current_key = f"calculate-{hallticket}-{degree}-{examCode}-{etype}-{type}-{result}"
        redis_response = redis_client.get(current_key)

        if redis_response != None:
            redis_out = json.loads(redis_response)
            results.append(redis_out)
        else:
            break
    else:
        print("DIDN'T CREATE A NEW KEY, GOT RESULTS FROM HALLTICKETS CACHED")
        return Response(json.dumps(results), mimetype='application/json')

    redis_client.set(hallticket_from + hallticket_to + examCode, json.dumps({"result":"loading"}))
    redis_client.expire(hallticket_from+hallticket_to+examCode, timedelta(minutes=10))

    def worker(start, end):
        results = []
        print("WORKER IS RUNNING")
        # Start the worker from here

        for i in range(start, end+1):
            hallticket = get_hallticket_helper(roll_number, i)
            print(hallticket)
            current_key = f"calculate-{hallticket}-{degree}-{examCode}-{etype}-{type}-{result}"
            redis_response = redis_client.get(current_key)

            if redis_response != None:
                redis_out = json.loads(redis_response)
                results.append(redis_out)
            else:
                # Perform the manaual fetch
                try:
                    resp = old_scrapper.get_result_with_url(
                        hallticket, dob, degree, examCode, etype, type, result)
                    new_res = calculate_sgpa(resp)
                    results.append(new_res)
                    redis_client.set(current_key, json.dumps(new_res))
                    redis_client.expire(current_key, timedelta(minutes=30))
                except Exception as e:
                    print(e)
                    redis_client.set(
                        current_key, json.dumps({hallticket: "FALSE"}))
                    redis_client.expire(current_key, timedelta(minutes=30))


        redis_client.set(hallticket_from+hallticket_to+examCode, json.dumps(results))
        redis_client.expire(hallticket_from+hallticket_to+examCode, timedelta(minutes=10))

    threading.Thread(target=worker, args=(start, end)).start()


    # This is only going to return in the first call.
    return Response(redis_client.get(hallticket_from + hallticket_to + examCode),  mimetype='application/json')


@app.route("/new/", methods=["GET"])
def all_unordered_results():
    _, _, _, unordered_results = new_scrapper.get_all_results()
    return Response(json.dumps(unordered_results),  mimetype='application/json')


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

    return Response(json.dumps(result),   mimetype='application/json')


if __name__ == "__main__":
    app.run()
