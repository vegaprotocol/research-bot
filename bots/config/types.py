import os
import os.path

from dataclasses import dataclass
from typing import Optional


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
    )

    return config