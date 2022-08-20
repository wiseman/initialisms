from decoder import Decoder
import json
from flask import Flask, request, render_template

# because aws looks for application
application = app = Flask(__name__)


@app.route("/")
def healthCheck():
    return render_template(
        "helt.html",
        title="Good start",
    )


@app.route("/api/mnemonics_function")
def returnListOfMnemonics():
    initials = request.args.get("i")
    ordered = True if (request.args.get("o") == "1") else False
    decoder = Decoder(ordered)
    return {"mnemonics_found": json.dumps(decoder.decode(initials.lower()))}


if __name__ == '__main__':
    app.run()
