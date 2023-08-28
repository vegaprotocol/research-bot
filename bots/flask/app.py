from flask import Flask
from typing import Callable

app = Flask(__name__)

def configure_flask(debug: bool):
    if debug:
        app.config.update(
            ENVIRONMENT = "development",
            FLASK_DEBUG = True,
        )
    else:
        app.config.update(
            ENVIRONMENT = "production",
            FLASK_DEBUG = False,
        )

    app.config['FLASK_APP'] = "research-bots"

@app.route("/health")
def health_check():
    return "OK"

def handler(path: str, handler_func: Callable):
    app.add_url_rule(view_func=handler_func, rule=path)