from service import Crawler
import json
import markdown, markdown.extensions.fenced_code
from pygments.formatters import HtmlFormatter
from flask import Flask, Response, request

# Initializing the Crawler object from service
scrapper = Crawler()

app = Flask(__name__)


@app.route("/")
def index():

    formatter = HtmlFormatter(full=True,cssclass="codehilite")
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

    result = scrapper.get_result(hallticket, dob, year)
    return Response(json.dumps(result),  mimetype='application/json')


@app.route("/result", methods=["GET"])
def request_param_path():

    hallticket = request.args.get("hallticket")
    dob = request.args.get("dob")
    year = request.args.get("year")

    result = scrapper.get_result(hallticket, dob, year)

    return Response(json.dumps(result),  mimetype='application/json')


if __name__ == "__main__":
    app.run()
