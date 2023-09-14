import flask
import logging
import json
import bots.config.types
import bots.api.datanode
import bots.config.types

from vega_sim.devops.wallet import ScenarioWallet
from typing import Optional
from bots.api.helpers import by_key
from bots.http.handler import Handler
from vega_sim.wallet.vega_wallet import VegaWallet

# wallet_names = [
#     "market_creator",
#     "market_settler",
#     "market_maker",
#     "auction_trader_a",
#     "auction_trader_b",
#     "random_trader_a",
#     "random_trader_b",
#     "random_trader_c",
#     "sensitive_trader_a",
#     "sensitive_trader_b",
#     "sensitive_trader_c",
# ]

# wallets_to_config_mapping = {
#     "market_creator": None,
#     "market_settler": None,
#     "market_maker": "market_maker_args",
#     "auction_trader_a": "auction_trader_args",
#     "auction_trader_b": "auction_trader_args",
#     "random_trader_a": "random_trader_args",
#     "random_trader_b": "random_trader_args",
#     "random_trader_c": "random_trader_args",
#     "sensitive_trader_a": "sensitive_trader_args",
#     "sensitive_trader_b": "sensitive_trader_args",
#     "sensitive_trader_c": "sensitive_trader_args",
# }

def is_trader(wallet_name: str) -> bool:
    trader_names = ["market_maker", "auction_trader", "random_trader", "sensitive_trader"]
    return any([ trader_name in wallet_name for trader_name in trader_names])

def get_config_attr_name(wallet_name: str) -> str:
    trader_names = ["market_maker", "auction_trader", "random_trader", "sensitive_trader"]
    for trader_name in trader_names:
        if trader_name in wallet_name:
            return trader_name

    raise RuntimeError(f"Attribute unknown for {wallet_name}")


class Traders(Handler):
    logger = logging.getLogger("report-traders")

    def __init__(self, 
                 host: str, 
                 port: int, 
                 scenarios: bots.config.types.ScenariosConfigType, 
                 api_endpoints: list[str], 
                 wallet: VegaWallet, 
                 wallet_name: str,
                 scenario_wallets: dict[str, ScenarioWallet],
    ):
        self.host = host
        self.port = port
        self.webserver = None
        self.scenarios = scenarios
        self.api_endpoints = api_endpoints
        self.wallet = wallet
        self.wallet_name = wallet_name
        self.scenario_wallets = scenario_wallets

        # TODO: filter by valid market statuses
        self.markets = by_key(bots.api.datanode.get_markets(api_endpoints), lambda market: market["tradableInstrument"]["instrument"]["name"])
        self.assets = by_key(bots.api.datanode.get_assets(api_endpoints), lambda asset: asset["id"])

        self.response_cache = None 

    def serve(self):
        if self.response_cache is None:
            Traders.logger.info("Refreshing cache for traders response")
            self.response_cache = self.prepare_response()
        else:
            Traders.logger.info("Serving traders response from cache")

        json_data = json.dumps({"traders": self.response_cache}, indent="    ")
        resp = flask.Response(json_data)
        resp.headers['Content-Type'] = 'application/json'
        return resp
    
    def prepare_response(self) -> dict[str, dict[str, any]]:
        traders = dict()
        # wallet_keys = self.wallet.get_keypairs(self.wallet_name)
        # missing_wallets = [ wallet_name for wallet_name in wallet_names if not wallet_name in wallet_keys ]
        # if len(missing_wallets) > 0:
        #     Traders.logger.error(f"Missing wallets {missing_wallets}")

        for scenario in self.scenarios:
            scenario_config = self.scenarios[scenario]
            scenario_market_name = scenario_config.market_name
            if not scenario_market_name in self.markets:
                Traders.logger.error(f"Market {scenario_market_name} not found in market downloaded from API, traders cannot be reported. There is a config for given market_name")

            scenario_market = self.markets[scenario_market_name]
            vega_asset_id = self._vega_asset_id_for_market(scenario_market)
            market_id = scenario_market["id"]
            market_tags = self._metadata_for_market(scenario_market)

            base = market_tags["ticker"] if "ticker" in market_tags else ""
            base = market_tags["base"] if "base" in market_tags else base
            scenario_asset = self.assets[vega_asset_id]
            # market is not for erc20 asset?
            if not "erc20" in scenario_asset["details"]:
                continue
            
            wallet_keys = self.wallet.get_keypairs(scenario)

            for wallet_name in wallet_keys:
                if not is_trader(wallet_name):
                    continue

                trader_params = getattr(scenario_config, get_config_attr_name(wallet_name))

                traders[f"{market_id}_{wallet_name}"] = {
                    "name": f"{market_id}_{wallet_name}",
                    "pubKey": wallet_keys[wallet_name],
                    "parameters": {
                        "marketBase": base,
                        "marketQuote": market_tags["quote"] if "quote" in market_tags else "",
                        "marketSettlementEthereumContractAddress": scenario_asset["details"]["erc20"]["contractAddress"],
                        "marketSettlementVegaAssetID": vega_asset_id,
                        "wanted_tokens": trader_params.initial_mint,
                        "balance": "tbd",
                    }
                }

        return traders

    
    def _vega_asset_id_for_market(self, market: dict[str, any]) -> Optional[str]:
        if not "tradableInstrument" in market:
            return None

        if not "instrument" in market["tradableInstrument"]:
            return None
        
        if "future" in market["tradableInstrument"]["instrument"]:
            return market["tradableInstrument"]["instrument"]["future"]["settlementAsset"]
        
        if "perpetual" in market["tradableInstrument"]["instrument"]:
            return market["tradableInstrument"]["instrument"]["perpetual"]["settlementAsset"]
        
    def _metadata_for_market(self, market: dict[str, any]) -> dict[str, str]:
        if not "tradableInstrument" in market:
            return dict()
        if not "instrument" in market["tradableInstrument"]:
            return dict()
        if not "metadata" in market["tradableInstrument"]["instrument"]:
            return dict()
        if not "tags" in market["tradableInstrument"]["instrument"]["metadata"]:
            return dict()
        
        return {
            item.split(":")[0]: item.split(":")[1] 
            for item in market["tradableInstrument"]["instrument"]["metadata"]["tags"] 
            if len(item.split(":")) >= 2}

def from_config(config: bots.config.types.BotsConfig, wallet_svc: VegaWallet, scenario_wallets: dict[str, ScenarioWallet]) -> Traders:
    return Traders(
        host=config.http_server.interface,
        port=config.http_server.port,
        scenarios=config.scenarios,
        api_endpoints=config.network_config.api.rest.hosts,
        wallet=wallet_svc,
        wallet_name=config.wallet.wallet_name,
        scenario_wallets=scenario_wallets,
    )