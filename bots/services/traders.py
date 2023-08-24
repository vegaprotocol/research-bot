import logging
import bots.config.types
import bots.api.datanode

from typing import Optional
from bots.api.helpers import by_key
from bots.services.service import Service
from http.server import BaseHTTPRequestHandler, HTTPServer
from bots.services.multiprocessing import threaded


class Traders(Service):
    logger = logging.getLogger("report-traders")

    def __init__(self, host: str, port: int, scenarios: bots.config.types.ScenariosConfigType, api_endpoints: list[str]):
        self.host = host
        self.port = port
        self.webserver = None
        self.scenarios = scenarios
        self.api_endpoints = api_endpoints

        self.markets = by_key(bots.api.datanode.get_markets(api_endpoints), lambda market: market["tradableInstrument"]["instrument"]["name"])
        self.assets = by_key(bots.api.datanode.get_assets(api_endpoints), lambda asset: asset["id"])
        
    def run(self):
        """
        Run the /traders server
        """

        trader = self

        class TradersHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                Traders.logger.info("%s - - [%s] %s\n" %
                                    (self.client_address[0],
                                    self.log_date_time_string(),
                                    format%args))
                

            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes("Traders", "utf-8"))
        
        Traders.logger.info(f"Starting server")
        self.webserver = HTTPServer((self.host, self.port), TradersHandler)
        Traders.logger.info("Server started at %s:%s" % (self.host, self.port))
        self.webserver.serve_forever()
        print("Server stopped.")

    def __del__(self):
        Traders.logger.info(f"Stopping server")
        if not self.webserver is None:
            self.webserver.server_close()
            Traders.logger.info(f"server stopped")
        else:
            Traders.logger.info(f"Server has not been running")

    def prepare_response(self) -> dict[str, dict[str, any]]:
        traders = dict()
        for scenario in self.scenarios:
            scenario_market_name = scenario["market_name"] 
            if not scenario_market_name in self.markets:
                Traders.logger.error(f"Market {scenario_market_name} not found in market downloaded from API, traders cannot be reported. There is a config for given market_name")
            
            
            scenario_market = self.markets[scenario_market_name]
            vega_asset_id = self._vega_asset_id_for_market(scenario_market)
            
    
    def _vega_asset_id_for_market(market: dict[str, any]) -> Optional[str]:
        if not "tradableInstrument" in market:
            return None

        if not "instrument" in market["tradableInstrument"]:
            return None
        
        if "future" in market["tradableInstrument"]["instrument"]:
            return market["tradableInstrument"]["instrument"]["future"]["settlementAsset"]
        
        if "perpetual" in market["tradableInstrument"]["instrument"]:
            return market["tradableInstrument"]["instrument"]["perpetual"]["settlementAsset"]


    @threaded
    def start(self):
        self.run()

def from_config(http_config: dict[str, any], scenarios: bots.config.types.ScenariosConfigType, api_endpoints: list[str]) -> Traders:
    return Traders(
        host=http_config.get("host", "0.0.0.0"),
        port=int(http_config.get("port", 8080)),
        scenarios=scenarios,
        api_endpoints=api_endpoints,
    )