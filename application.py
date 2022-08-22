from decoder import Decoder
import json
from flask import Flask, request, render_template, jsonify, make_response
from flask_cors import CORS

# because aws looks for application
application = app = Flask(__name__)
CORS(app)


@app.route("/")
def healthCheck():
    return render_template(
        "helt.html",
        title="Good start",
    )


@app.route("/api/mnemonics_function")
def returnListOfMnemonics():
    print("request.args = ", request.args)
    initials = request.args.get("i")
    ordered = True if (request.args.get("o") == "1") else False
    decoder = Decoder(ordered)
    resp = make_response(
        jsonify({"mnemonics_found": json.dumps(decoder.decode(initials.lower()))})
        )
    # TODO this should be set to the actual origins, i.e. maxyourmarks.com
    resp.headers["Access-Control-Allow-Methods"] = "GET, OPTION"
    resp.headers["Access-Control-Allow-Headers"] = "Origin"
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers["Content-Type"] = "application/json"

    return resp


if __name__ == '__main__':
    app.debug = True
    app.run()
