import requests
import logging

def get_call(endpoint: str) -> any:
    endpoint_url = endpoint if "http" in endpoint else f"https://{endpoint}"

    logging.debug(f"Making GET call to {endpoint_url}")
    resp = requests.get(endpoint_url)
    if resp.status_code != 200:
        logging.debug(f"Invalid response from {endpoint_url}. Expected status code 200, got {resp.status_code}")
        raise requests.HTTPError(f"Invalid response code. Expected 200, got {resp.status_code}")

    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        err = str(e)
        logging.debug(f"Failed to get response from {endpoint_url}: {err}")
        raise e
    return resp.json()