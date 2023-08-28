import logging
import json
import bots.config.types
import bots.api.datanode
import bots.config.types
import multiprocessing

from typing import Optional
from bots.api.helpers import by_key
from bots.flask.handler import Handler
from bots.vega_sim.wallet import from_config as vega_sim_wallet_from_config
from vega_sim.wallet.vega_wallet import VegaWallet

wallet_names = [
    "market_creator",
    "market_settler",
    "market_maker",
    "auction_trader_a",
    "auction_trader_b",
    "random_trader_a",
    "random_trader_b",
    "random_trader_c",
    "sensitive_trader_a",
    "sensitive_trader_b",
    "sensitive_trader_c",
]

class Traders(Handler):
    logger = logging.getLogger("report-traders")

    def __init__(self, host: str, port: int, scenarios: bots.config.types.ScenariosConfigType, api_endpoints: list[str], wallet: VegaWallet, wallet_name: str):
        self.host = host
        self.port = port
        self.webserver = None
        self.scenarios = scenarios
        self.api_endpoints = api_endpoints
        self.wallet = wallet
        self.wallet_name = wallet_name

        # TODO: filter by valid market statuses
        self.markets = by_key(bots.api.datanode.get_markets(api_endpoints), lambda market: market["tradableInstrument"]["instrument"]["name"])
        self.assets = by_key(bots.api.datanode.get_assets(api_endpoints), lambda asset: asset["id"])

        self.response_cache = None 

    def serve(self):
        if self.response_cache is None:
            self.response_cache = self.prepare_response()

        return json.dumps({"traders": self.response_cache}, indent="    ")
    
    def prepare_response(self) -> dict[str, dict[str, any]]:
        traders = dict()
        wallet_keys = self.wallet.get_keypairs(self.wallet_name)
        missing_wallets = [ wallet_name for wallet_name in wallet_names if not wallet_name in wallet_keys ]
        if len(missing_wallets) > 0:
            Traders.logger.error(f"Missing wallets {missing_wallets}")

        for scenario in self.scenarios:
            scenario_market_name = scenario["market_name"] 
            if not scenario_market_name in self.markets:
                Traders.logger.error(f"Market {scenario_market_name} not found in market downloaded from API, traders cannot be reported. There is a config for given market_name")
            
            for wallet_name in wallet_names:
                if wallet_name in missing_wallets:
                    continue

                scenario_market = self.markets[scenario_market_name]
                vega_asset_id = self._vega_asset_id_for_market(scenario_market)
                market_id = scenario_market["id"]
                traders[f"{market_id}_{wallet_name}"] = {
                    "name": f"{market_id}_{wallet_name}",
                    "pubKey": wallet_keys[wallet_name],
                    "parameters": {
                        "marketBase": "AAVE",
                        "marketQuote": "DAI",
                        "marketSettlementEthereumContractAddress": "0x973cB2a51F83a707509fe7cBafB9206982E1c3ad",
                        "marketSettlementVegaAssetID": "b340c130096819428a62e5df407fd6abe66e444b89ad64f670beb98621c9c663",

                    }
                }
            

        return traders

    
    def _vega_asset_id_for_market(market: dict[str, any]) -> Optional[str]:
        if not "tradableInstrument" in market:
            return None

        if not "instrument" in market["tradableInstrument"]:
            return None
        
        if "future" in market["tradableInstrument"]["instrument"]:
            return market["tradableInstrument"]["instrument"]["future"]["settlementAsset"]
        
        if "perpetual" in market["tradableInstrument"]["instrument"]:
            return market["tradableInstrument"]["instrument"]["perpetual"]["settlementAsset"]

def from_config(config: bots.config.types.BotsConfig, wallet_mutex: Optional[multiprocessing.Lock]) -> Traders:
    return Traders(
        host=config.http_server.interface,
        port=config.http_server.port,
        scenarios=config.scenarios,
        api_endpoints=config.network_config.api.rest.hosts,
        wallet=vega_sim_wallet_from_config(config.wallet, wallet_mutex),
        wallet_name=config.wallet.wallet_name,
    )