from service import Crawler
import json
from flask import Flask, Response, request

# Initializing the Crawler object from service
scrapper = Crawler()

app = Flask(__name__)


@app.route("/<hallticket>/<dob>/<year>")
def index(hallticket, dob, year):

    # hallticket = request.args.get("hallticket")
    # dob = request.args.get("dob")
    # year = request.args.get("year")

    result = scrapper.get_result(hallticket, dob, year)
    # print(result)
    return Response(json.dumps(result),  mimetype='application/json')


if __name__ == "__main__":
    app.run()
