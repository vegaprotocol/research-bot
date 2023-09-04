import requests
import logging

from bots.api.http import get_call

def get_markets(endpoints: list[str]) -> any:
    for endpoint in endpoints:
        try:
            json_resp = get_call(f"{endpoint}/api/v2/markets")
        except:
            continue

        if not "markets" in json_resp:
            continue

        return [ market["node"] for market in json_resp["markets"]["edges"] ]

    raise requests.RequestException("all endpoints for /api/v2/markets did not return a valid response")


def check_market_exists(endpoints: list[str], market_names: list[str]):
    all_markets = get_markets(endpoints)
    all_markets_names = [market["tradableInstrument"]["instrument"]["name"] for market in all_markets]
    
    for required_market_name in market_names:
        if not required_market_name in all_markets_names:
            raise EnvironmentError(f"The market \"{required_market_name}\" is missing, it is required to exist on the network. Modify the config.toml file to correct the data.")

def get_statistics(endpoints: list[str]) -> dict[str, any]:
    for endpoint in endpoints:
        try:
            json_resp = get_call(f"{endpoint}/statistics")
        except:
            continue

        if not "statistics" in json_resp:
            continue

        return json_resp["statistics"]

    raise requests.RequestException("all endpoints for /statistics did not return a valid response")

def get_assets(endpoints: list[str]) -> dict[str, any]:
    for endpoint in endpoints:
        try:
             json_resp = get_call(f"{endpoint}/api/v2/assets")
        except:
            continue

        if not "assets" in json_resp:
            continue

        return [ asset["node"] for asset in json_resp["assets"]["edges"] ]

    raise requests.RequestException("all endpoints for /statistics did not return a valid response")
