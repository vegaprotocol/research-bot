import requests
import logging
import bots.api.types


from typing import Optional
from bots.api.http import get_call


def get_max_core_height(endpoints: list[str]) -> int:
    max_height = 0
    for endpoint in endpoints:
        try:
            # get statistics for each endpoints
            stats = get_statistics([endpoint])
            if "blockHeight" in stats and int(stats["blockHeight"]) > max_height:
                max_height = int(stats["blockHeight"])
        except:
            pass  # we do not care about errors here...

    if max_height < 1:
        raise requests.RequestException(
            "cannot get max network height, all available nodes did not return valid response for the /statistics endpoint"
        )

    return max_height


def get_healthy_endpoints(endpoints: list[str]) -> list[str]:
    max_allowed_lag_blocks = 500
    result = []

    max_core_height = get_max_core_height(endpoints)

    for endpoint in endpoints:
        try:
            stats = get_statistics([endpoint])

            if not "blockHeight" in stats:
                continue

            core_height = int(stats["blockHeight"])
            if core_height < max_core_height and max_core_height - core_height > max_allowed_lag_blocks:
                continue

            # if data-node check its block as well
            if "x-block-height" in stats:
                data_node_height = int(stats["x-block-height"])

                if data_node_height < max_core_height and max_core_height - data_node_height > max_allowed_lag_blocks:
                    continue

            result.append(endpoint)
        except:
            pass

    return result


def get_markets(endpoints: list[str]) -> any:
    for endpoint in endpoints:
        try:
            json_resp = get_call(f"{endpoint}/api/v2/markets")[0]
        except:
            continue

        if not "markets" in json_resp:
            continue

        return [market["node"] for market in json_resp["markets"]["edges"]]

    raise requests.RequestException("all endpoints for /api/v2/markets did not return a valid response")


def check_market_exists(endpoints: list[str], market_names: list[str]):
    all_markets = get_markets(endpoints)
    all_markets_names = [market["tradableInstrument"]["instrument"]["name"] for market in all_markets]

    for required_market_name in market_names:
        if not required_market_name in all_markets_names:
            raise EnvironmentError(
                f'The market "{required_market_name}" is missing, it is required to exist on the network. Modify the config.toml file to correct the data.'
            )


def get_statistics(endpoints: list[str]) -> dict[str, any]:
    response = ([], dict())
    for endpoint in endpoints:
        try:
            response = get_call(f"{endpoint}/statistics")
        except:
            continue

        if len(response) < 1 or "statistics" not in response[0]:
            continue

        result = response[0]["statistics"]
        # append data-node height to the response
        if len(response) > 1 and "x-block-height" in response[1]:
            result["x-block-height"] = response[1]["x-block-height"]

        return result

    raise requests.RequestException("all endpoints for /statistics did not return a valid response")


def get_assets(endpoints: list[str]) -> dict[str, any]:
    for endpoint in endpoints:
        try:
            json_resp = get_call(f"{endpoint}/api/v2/assets")[0]
        except:
            continue

        if not "assets" in json_resp:
            continue

        return [asset["node"] for asset in json_resp["assets"]["edges"]]

    raise requests.RequestException("all endpoints for /statistics did not return a valid response")


def get_accounts(
    endpoints: list[str],
    asset_id: Optional[str] = None,
    parties: Optional[list[str]] = None,
    market_ids: Optional[list[str]] = None,
    afterCursor: Optional[str] = None,
) -> list[bots.api.types.Account]:
    query = []

    if not asset_id is None:
        query = query + [f"filter.assetId={asset_id}"]

    if not parties is None:
        parties_list = ",".join(parties)
        query = query + [f"filter.partyIds={parties_list}"]

    if not market_ids is None:
        markets_list = ",".join(market_ids)
        query = query + [f"filter.marketIds={markets_list}"]

    if not afterCursor is None:
        query = query + [f"pagination.after={afterCursor}"]

    url = "api/v2/accounts"

    if len(query) > 0:
        query_str = "&".join(query)
        url = f"{url}?{query_str}"

    for endpoint in endpoints:
        try:
            json_resp = get_call(f"{endpoint}/{url}")[0]
        except:
            continue

        if not "accounts" in json_resp:
            continue

        response = []
        for edge in json_resp["accounts"]["edges"]:
            if not "node" in edge:
                continue
            response.append(
                bots.api.types.Account(
                    owner=edge["node"]["owner"],
                    balance=int(edge["node"]["balance"]),
                    asset=edge["node"]["asset"],
                    market_id=edge["node"]["marketId"],
                    type=edge["node"]["type"],
                )
            )

        if (
            "pageInfo" in json_resp["accounts"]
            and "hasNextPage" in json_resp["accounts"]["pageInfo"]
            and json_resp["accounts"]["pageInfo"]["hasNextPage"]
        ):
            return response + get_accounts(
                endpoints, asset_id, parties, market_ids, json_resp["accounts"]["pageInfo"]["endCursor"]
            )

        return response

    raise requests.RequestException("all endpoints for /api/v2/assets did not return a valid response")
