import os
import urllib.parse
import urllib.request
import tomllib

from dataclasses import dataclass
from typing import Optional
from bots.config.config import is_valid_url, logger

@dataclass
class AppsNetworkConfig:
    console: Optional[str]
    governance: Optional[str]
    explorer: Optional[str]

@dataclass
class ApplicationNetworkConfig:
    local_port: Optional[int]
    url: Optional[str]

@dataclass
class ProtocolAPINetworkConfig:
    hosts: list[str]
    retries: Optional[int]

@dataclass
class APINetworkConfig:
    rest: ProtocolAPINetworkConfig
    grpc: ProtocolAPINetworkConfig
    graph_ql: ProtocolAPINetworkConfig

@dataclass
class NetworkConfig:
    file_path: str
    file_version: int
    host: Optional[str]
    level: Optional[str]
    name: str
    port: int
    token_expiry: Optional[str]

    metadata: dict[str, str]

    api: APINetworkConfig
    apps: AppsNetworkConfig


def api_network_config_from_dict(data: dict[str, any]) -> ProtocolAPINetworkConfig:
    retries = data.get('Retries', None)

    return ProtocolAPINetworkConfig(
        hosts=data.get("Hosts", []),
        retries=int(retries) if not retries is None else None
    )

def apps_network_config_from_dict(data: dict[str, any]) -> AppsNetworkConfig:
    return AppsNetworkConfig(
        console=data.get("Console", None),
        governance=data.get("Governance", None),
        explorer=data.get("Explorer", None)
    )

def network_config_from_dict(path: str, data: dict[str, any]) -> NetworkConfig:
    return NetworkConfig(
        file_path=path,
        file_version=int(data.get("FileVersion", 1)),
        host=data.get("Host", None),
        level=data.get("Level", None),
        name=data.get("Name", ""),
        port=int(data.get("Port", 1789)),
        token_expiry=data.get("TokenExpiry", None),
        
        api=APINetworkConfig(
            grpc=api_network_config_from_dict(data["API"]["GRPC"]),
            rest=api_network_config_from_dict(data["API"]["REST"]),
            graph_ql=api_network_config_from_dict(data["API"]["GraphQL"]),
        ),

        metadata={
            metadata.get("Key"): metadata.get("Value") 
            for metadata in data.get("Metadata", []) if "Key" in metadata and "Value" in metadata
        },

        apps=apps_network_config_from_dict(data.get("Apps", dict())),
    )


def _local_network_config_path(path: str, devops_network_name: str, base_dir: str) -> str:
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

def load_network_config(path: str, devops_network_name: str, base_dir: str) -> NetworkConfig:
    local_config_path = _local_network_config_path(path, devops_network_name, base_dir)

    data = None
    with open(local_config_path, "rb") as f:
        data = tomllib.load(f)

    return network_config_from_dict(local_config_path, data)