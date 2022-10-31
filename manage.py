from flask import g
from flask import request
from flask import session
from flask_siwadoc import SiwaDoc

from piscis.exception import Success
from piscis.exception import UnAuthentication

from app import create_app
from config.code_message import MESSAGE


app = create_app(config_message=MESSAGE)




@app.route("/ping")
def ping():
    return Success("test")


if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)
