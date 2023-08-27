import logging
import bots.config.types


from bots.services.service import Service
from http.server import BaseHTTPRequestHandler, HTTPServer
from bots.services.multiprocessing import threaded


class DefaultHealthCheckHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        HealthCheckService.logger.info("%s - - [%s] %s\n" %
                            (self.client_address[0],
                             self.log_date_time_string(),
                             format%args))
        

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("OK", "utf-8"))

class HealthCheckService(Service):
    logger = logging.getLogger("health-check")

    def __init__(self, host: str, port: int, handler: BaseHTTPRequestHandler=DefaultHealthCheckHandler):
        self.host = host
        self.port = port
        self.handler = handler

        self.webserver = None

    def run(self):
        """
        Run the  health-check server
        """
        
        HealthCheckService.logger.info(f"Starting server")
        self.webserver = HTTPServer((self.host, self.port), self.handler)
        HealthCheckService.logger.info("Server started at %s:%s" % (self.host, self.port))
        self.webserver.serve_forever()
        print("Server stopped.")

    def __del__(self):
        HealthCheckService.logger.info(f"Stopping server")
        if not self.webserver is None:
            self.webserver.server_close()
            HealthCheckService.logger.info(f"server stopped")
        else:
            HealthCheckService.logger.info(f"Server has not been running")

    @threaded
    def start(self):
        self.run()

def from_config(config: bots.config.types.HttpServerConfig) -> HealthCheckService:
    return HealthCheckService(
        host=config.interface,
        port=config.port,
    )