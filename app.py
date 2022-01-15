from datetime import timedelta
import json
import os
import platform

from flask import Flask, Response, request
import markdown
import markdown.extensions.fenced_code
from pygments.formatters import HtmlFormatter
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

    sgpa = round(sgpa/total_credits, 2)
    results_object.insert(0, {"SGPA": sgpa if sgpa else "FAIL"})

    return results_object


app = Flask(__name__)


@app.route("/")
def index():

    formatter = HtmlFormatter(full=True, cssclass="codehilite")
    css_string = formatter.get_style_defs()
    readme = open("README_PAGE.md", "r")
    md_template = markdown.markdown(
        readme.read(), extensions=["fenced_code", "codehilite"]
    )
    md_css_string = "<style>" + css_string + "</style>"
    md_template = md_css_string + md_template
    return md_template


@app.route("/<hallticket>/<dob>/<year>", methods=["GET"])
def routing_path(hallticket, dob, year):
    current_key = f"{hallticket}-{year}"

    redis_response = redis_client.get(current_key)
    if redis_response != None:
        result = json.loads(redis_response)
    else:
        result = old_scrapper.get_result(hallticket, dob, year)
        redis_client.set(current_key, json.dumps(result))
        redis_client.expire(current_key, timedelta(days=1))

    return Response(json.dumps(result),  mimetype='application/json')


@app.route("/calculate/<hallticket>/<dob>/<year>", methods=["GET"])
def calculate(hallticket, dob, year):
    current_key = f"calculate-{hallticket}-{year}"

    redis_response = redis_client.get(current_key)
    if redis_response != None:
        result = json.loads(redis_response)
    else:
        result = old_scrapper.get_result(hallticket, dob, year)
        result = calculate_sgpa(result)
        redis_client.set(current_key, json.dumps(result))
        redis_client.expire(current_key, timedelta(days=1))

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
        redis_client.set(current_key, json.dumps(result))
        redis_client.expire(current_key, timedelta(days=1))

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
        redis_client.set(current_key, json.dumps(resp))
        redis_client.expire(current_key, timedelta(days=1))

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
        result = calculate_sgpa(resp)
        redis_client.set(current_key, json.dumps(result))
        redis_client.expire(current_key, timedelta(days=1))

    return Response(json.dumps(result),  mimetype='application/json')


@app.route("/new/", methods=["GET"])
def all_unordered_results():
    _, _, _, unordered_results = new_scrapper.get_all_results()
    return Response(json.dumps(unordered_results),  mimetype='application/json')


@app.route("/notifications", methods=["GET"])
def notifications():
    current_key = "notifications"

    redis_response = redis_client.get(current_key)
    if redis_response != None:
        result = json.loads(redis_response)
    else:
        result = new_scrapper.get_notifiations()
        redis_client.set(current_key, json.dumps(result))
        redis_client.expire(current_key, timedelta(minutes=30))

    return Response(json.dumps(result),   mimetype='application/json')


if __name__ == "__main__":
    app.run()
