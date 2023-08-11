import tomllib
import urllib
import urllib.parse

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
    with urllib.urlopen(url) as config_content:
        data = tomllib.loads(config_content, parse_float=float)
    
    if data is None:
        raise Exception("No config was returned from URL")
    
def read_config(path: str) -> dict[str, any]:
    if is_valid_url(path):
        return _read_config_from_url(path)

    return _read_config_from_file(path)