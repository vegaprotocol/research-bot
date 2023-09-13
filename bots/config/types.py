import os
import os.path
import tomllib
import urllib.request

from dataclasses import dataclass
from typing import Optional
from bots.config.config import is_valid_url, read_config_from_file, read_config_from_url, logger

def _market_sim_network_from_devops_network_name(net_name: str) -> str:
    mapping = {
        "devnet1": "DEVNET1",
        "stagnet1": "STAGNET1",
        "fairground": "FAIRGROUND",
        "mainnet-mirror": "MAINNET_MIRROR",
        "mainnet_mirror": "MAINNET_MIRROR"
    }

    if not net_name in mapping:
        return net_name

    return mapping[net_name]


ScenariosConfigType = dict[str, dict[str, any]]



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

@dataclass
class WalletConfig:
    # Version of the vega wallet, ignored if download_wallet_binary == false, or auto_version = True
    version: Optional[str]
    # Repository where we search specific release for vegawallet
    repository: Optional[str]
    # The artifact name to download (vegawallet, or vega)
    artifact_name: str
    # Enable/disable auto download feature
    download_wallet_binary: bool
    # When true, wallet version is obtained from the /statistics endpoint from the appVersion value
    auto_version: bool
    # The name of the wallet to use by bots
    wallet_name: str
    # The network name
    network_name: str
    # binary path, this will be used when download_wallet_binary = False. Can be string(e.g: vegawallet), or list of strings(e.g: ["vegawallet"], or ["vega", "wallet"])
    binary: str | list[str]
    # Path of the vega wallet home
    home: str
    # The wallet passphrase file path
    passphrase_file: str
    # Wallet URL
    wallet_url: str

    def update_binary(self, binary_override: str | list[str]):
        self.binary = binary_override

@dataclass
class HttpServerConfig:
    # IP for listening http servers, e.g: 0.0.0.0 or 127.0.0.1
    interface: str
    # Port, where HTTP servers listen
    port: int


@dataclass
class BotsConfig:
    # Path for the network config(aka wallet toml config), local file path or URL
    network_config_file: str
    # Enable/disable debug for logs
    debug: bool
    # Path for the work dir, where We download files and creates temp files
    work_dir: str

    # wallet config
    wallet: WalletConfig
    # http server config
    http_server: HttpServerConfig
    # scenarios config
    scenarios: ScenariosConfigType

    # The network name used in devops scripts and repositories
    devops_network_name: str
    # The network name used in the vega-market-sim library
    vega_market_sim_network_name: str

    # Network config, aka wallet toml config
    network_config: Optional[NetworkConfig]

    def update_network_config(self, cfg: NetworkConfig):
        self.network_config = cfg

def wallet_config_from_json(json: dict[str, any]) -> WalletConfig:
    passphrase_file = json.get("passphrase_file", "./assets/passphrase.txt")
    if not os.path.isabs(passphrase_file):
        passphrase_file = os.path.abspath(os.path.join(os.getcwd(), passphrase_file))

    wallet_home = json.get("home", "./wallethome")
    if not os.path.isabs(wallet_home):
        wallet_home =  os.path.abspath(os.path.join(os.getcwd(), wallet_home))

    return WalletConfig(
        version=json.get("version", None),
        repository=json.get("repository", None),
        artifact_name=json.get("artifact_name", "vegawallet"),
        download_wallet_binary=bool(json.get("download_wallet_binary", False)),
        auto_version=bool(json.get("auto_version", False)),
        wallet_name=json.get("wallet_name", "vegawallet"),
        network_name=json.get("network_name", ""),
        binary=json.get("binary", "vegawallet"),
        home=wallet_home,
        passphrase_file=passphrase_file,
        wallet_url=json.get("wallet_url", "http://127.0.0.1:1789")
    )

def http_server_config_from_json(json: dict[str, any]) -> HttpServerConfig:
    return HttpServerConfig(
        interface=json.get("interface", "0.0.0.0"),
        port=int(json.get("port", 8080)),
    )

def config_from_json(json: dict[str, any]) -> BotsConfig:
    work_dir = json.get("work_dir", "./network")
    if not os.path.isabs(work_dir):
        work_dir =  os.path.abspath(os.path.join(os.getcwd(), work_dir))

    wallet_config = wallet_config_from_json(json.get("vegawallet", dict()))
    config = BotsConfig(
        network_config_file=json.get("network_config_file", ""),
        debug=bool(json.get("debug", False)),
        work_dir=work_dir,

        wallet=wallet_config,
        http_server=http_server_config_from_json(json.get("http_server", dict())),
        scenarios=json.get("scenario", dict()),

        devops_network_name=wallet_config.network_name,
        vega_market_sim_network_name=_market_sim_network_from_devops_network_name(wallet_config.network_name),
        network_config=None,
    )

    return config

##
 # Network config aka wallet toml config
 ##

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


def read_bots_config(path: str) -> BotsConfig:
    config_json = None
    if is_valid_url(path):
        config_json =  read_config_from_url(path)
    else: 
        config_json = read_config_from_file(path)

    return config_from_json(config_json)