import requests

def get_markets(endpoints: list[str]) -> any:
    for endpoint in endpoints:
        endpoint_url = endpoint if "http" in endpoint else f"https://{endpoint}"

        resp = requests.get(f"{endpoint_url}/api/v2/markets")
        if resp.status_code != 200:
            continue

        json_resp = resp.json()

        if not "markets" in json_resp:
            continue

        return json_resp["markets"]

    raise requests.RequestException("all endpoints for /markets did not return a valid response")


def check_market_exists(endpoints: list[str], market_names: list[str]):
    all_markets = get_markets(endpoints)["edges"]
    all_markets_names = [market["node"]["tradableInstrument"]["instrument"]["name"] for market in all_markets]
    
    for required_market_name in market_names:
        if not required_market_name in all_markets_names:
            raise EnvironmentError(f"The market \"{required_market_name}\" is missing, it is required to exist on the network. Modify the config.toml file to correct the data.")
