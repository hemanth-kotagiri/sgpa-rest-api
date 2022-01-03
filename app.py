from service import Service
from all_results_service import AllResults
import json
import markdown
import markdown.extensions.fenced_code
from pygments.formatters import HtmlFormatter
from flask import Flask, Response, request

# Initializing the Crawler object from service
old_scrapper = Service()
new_scrapper = AllResults()

app = Flask(__name__)
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

    result = old_scrapper.get_result(hallticket, dob, year)
    return Response(json.dumps(result),  mimetype='application/json')


@app.route("/calculate/<hallticket>/<dob>/<year>", methods=["GET"])
def calculate(hallticket, dob, year):
    result = old_scrapper.get_result(hallticket, dob, year)
    # Calculating the result
    sgpa = 0
    total_credits = 0
    for subject in result[1]:
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
    result.insert(0, {"SGPA": sgpa if sgpa else "FAIL"})
    return Response(json.dumps(result),  mimetype='application/json')


@app.route("/result", methods=["GET"])
def request_param_path():

    hallticket = request.args.get("hallticket")
    dob = request.args.get("dob")
    year = request.args.get("year")

    result = old_scrapper.get_result(hallticket, dob, year)

    return Response(json.dumps(result),  mimetype='application/json')


@app.route("/new/all", methods=["GET"])
def all():
    result = new_scrapper.get_all_results()
    return Response(json.dumps(result),  mimetype='application/json')


if __name__ == "__main__":
    app.run()
