from piscis.exception import Success
from app import create_app
from config.code_message import MESSAGE

app = create_app(config_message=MESSAGE)


@app.route("/ping")
def ping():
    return Success("test")


if __name__ == "__main__":
    app.run(debug=True)
