import bots.config.types

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
@app.route("/status")
def health_check():
    return "OK"

def handler(path: str, handler_func: Callable):
    app.add_url_rule(view_func=handler_func, rule=path)

def run(debug: bool, http_config: bots.config.types.HttpServerConfig):
    port = http_config.port
    host = http_config.interface

    if http_config.port <= 0:
        port = 5000
    
    if http_config.interface is None or len(http_config.interface) < 1:
        host = "0.0.0.0"
    
    
    app.run(debug=debug, host=host, port=port)