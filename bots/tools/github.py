import zipfile
import platform
import logging
import os.path
import os
import stat

from io import BytesIO
from urllib.request import urlopen

def compose_asset_file_name(asset_type: str) -> str:
    processor = platform.processor().lower()
    system = platform.system().lower()

    processor = "amd64" if processor == "x86_64" else processor

    return f"{asset_type}-{system}-{processor}.zip"

def download_and_unzip_github_asset(asset_type: str, version: str, output_path: str, repository: str = "vegaprotocol/vega") -> None:    
    asset_file_name = compose_asset_file_name(asset_type)
    url = f"https://github.com/{repository}/releases/download/{version}/{asset_file_name}"
    logging.info(f"Downloading vegawallet binary from {url}")
    resp = urlopen(url)

    with zipfile.ZipFile(BytesIO(resp.read())) as zip:
        logging.info(f"Extracting vegawallet binary to {output_path}")
        zip.extractall(output_path)

    binary_path = os.path.join(output_path, asset_type)
    logging.info(f"Adding executable permissions for downloaded binary {binary_path}")

    st = os.stat(binary_path)
    os.chmod(binary_path, st.st_mode | stat.S_IEXEC)

    return binary_path