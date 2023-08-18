import tomllib
import os
import os.path
import logging
import tomllib
import urllib.request
import urllib.parse

logger = logging.getLogger("config")


def is_valid_url(x):
    try:
        result = urllib.parse.urlparse(x)
        return all([result.scheme, result.netloc])
    except:
        return False

def _read_config_from_file(file_path: str) -> dict[str, any]:
    data = None
    with open(file_path, "rb") as f:
        data = tomllib.load(f)

    if data is None:
        raise Exception("No config was returned from file")
    
    return data

def _read_config_from_url(url: str) -> dict[str, any]:
    data = None
    with urllib.request.urlopen(url) as response:
        config_content = response.read()
        data = tomllib.loads(config_content, parse_float=float)
    
    if data is None:
        raise Exception("No config was returned from URL")
    
def read_config(path: str) -> dict[str, any]:
    if is_valid_url(path):
        return _read_config_from_url(path)

    return _read_config_from_file(path)

def local_network_config_path(path: str, devops_network_name: str, base_dir: str) -> str:
    global logger

    if is_valid_url(path):
        if not os.path.isdir(base_dir):
            os.mkdir(base_dir)
        
        logger.info(f"Downloading network config from {path} to {base_dir}/vegawallet-{devops_network_name}.toml")

        file_path = os.path.join(base_dir, f"vegawallet-{devops_network_name}.toml")
        with urllib.request.urlopen(url=path, timeout=5.0) as response, open(file_path, "w") as f:
            config_content = response.read()
            f.write(config_content.decode('utf-8'))

        logger.info("The network config downloaded")
        return file_path
    
    # Add check for the file name
    if os.path.isfile(path):
        return path

    raise Exception("Network config does not exists")

def load_network_config_file(file_path: str) -> any:
    data = None
    with open(file_path, "rb") as f:
        data = tomllib.load(f)

    return data