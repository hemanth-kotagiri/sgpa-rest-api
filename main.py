from service import Crawler
import json
from flask import Flask, Response, jsonify

# Initializing the Crawler object from service
scrapper = Crawler()

# scrapper.get_result("185u1a0565", "2001-04-03", "1,1")
# scrapper.get_result("185u1a0565", "2001-04-03", "1,2")
# scrapper.get_result("185u1a0565", "2001-04-03", "2,1")

app = Flask(__name__)


@app.route("/")
def index():
    result = scrapper.get_result("185u1a0565", "2001-04-03", "1,1")
    return Response(json.dumps(result),  mimetype='application/json')


if __name__ == "__main__":
    app.run()
