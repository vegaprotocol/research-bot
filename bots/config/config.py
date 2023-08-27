import tomllib
import os
import os.path
import logging
import tomllib
import requests
import urllib.parse
import bots.config.types


logger = logging.getLogger("config")


def is_valid_url(x):
    try:
        result = urllib.parse.urlparse(x)
        return all([result.scheme, result.netloc])
    except:
        return False

def _read_config_from_file(file_path: str) -> dict[str, any]:
    logger.info(f"Reading bots config from local file: {file_path}")
    data = None
    with open(file_path, "rb") as f:
        data = tomllib.load(f)

    if data is None:
        raise Exception("No config was returned from file")
    
    return data

def _read_config_from_url(url: str) -> dict[str, any]:
    logger.info(f"Reading bots config from remote file: {url}")
    data = None

    resp = requests.get(url)
    data = tomllib.loads(resp.text, parse_float=float)
    
    if data is None:
        raise Exception("No config was returned from URL")
    
    return data
    
def read_config(path: str) -> bots.config.types.BotsConfig:
    config_json = None
    if is_valid_url(path):
        config_json =  _read_config_from_url(path)

    config_json = _read_config_from_file(path)

    return bots.config.types.config_from_json(config_json)