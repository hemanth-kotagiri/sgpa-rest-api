from service import Crawler
import json
from flask import Flask, Response, request

# Initializing the Crawler object from service
scrapper = Crawler()

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello, working"


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
    app.run(debug=False)
