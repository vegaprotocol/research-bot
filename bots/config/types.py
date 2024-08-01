import os
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
        "mainnet_mirror": "MAINNET_MIRROR",
    }

    if not net_name in mapping:
        return net_name

    return mapping[net_name]


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
    # Tokens file - file required by the vega-market-sim to read the wallet api token for specific wallet
    tokens_file: str
    # State file - file where all generated keys (mnemonics, public keys, are stored)
    state_file: str

    def update_binary(self, binary_override: str | list[str]):
        self.binary = binary_override


@dataclass
class HttpServerConfig:
    # IP for listening http servers, e.g: 0.0.0.0 or 127.0.0.1
    interface: str
    # Port, where HTTP servers listen
    port: int


@dataclass
class ScenarioMarketManagerConfig:
    asset_name: str
    adp: int
    mdp: int
    pdp: int


@dataclass
class ScenarioMarketMakerConfig:
    market_kappa: float
    market_kappa: float
    market_order_arrival_rate: int
    order_kappa: float
    order_size: int
    order_levels: int
    order_spacing: float
    order_clipping: int
    inventory_lower_boundary: int
    inventory_upper_boundary: int
    fee_amount: float
    commitment_amount: int
    initial_mint: int
    isolated_margin_factor: float


@dataclass
class ScenarioAuctionTraderConfig:
    traders: int

    initial_volume: float
    initial_mint: int


@dataclass
class ScenarioRandomTraderConfig:
    traders: int

    order_intensity: list[int]
    order_volume: list[float]
    step_bias: list[float]
    initial_mint: int


@dataclass
class ScenarioSensitiveTraderConfig:
    traders: int

    scale: list[int]
    max_order_size: list[float]
    initial_mint: int


@dataclass
class ScenarioSimulationConfig:
    n_steps: int
    granularity: str
    coinbase_code: str
    start_date: str
    randomise_history: bool


@dataclass
class ScenarioAutomatedMarketMaker:
    commitment_amount: int
    proposed_fee: float
    lower_bound_scaling: float
    upper_bound_scaling: float
    leverage_at_lower_bound: float
    leverage_at_upper_bound: float
    update_bias: float
    slippage_tolerance: float
    initial_mint: int


@dataclass
class ScenarioConfig:
    enable_top_up: bool
    market_name: str
    market_code: str
    price_symbol: str
    price_source: str
    feed_price_multiplier: int
    step_length_seconds: int

    market_manager: ScenarioMarketManagerConfig
    market_maker: ScenarioMarketMakerConfig
    automated_market_maker: ScenarioAutomatedMarketMaker
    auction_trader: ScenarioAuctionTraderConfig
    random_trader: ScenarioRandomTraderConfig
    sensitive_trader: ScenarioSensitiveTraderConfig
    simulation: ScenarioSimulationConfig


ScenariosConfigType = dict[str, ScenarioConfig]


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


def scenario_market_manager_config_from_json(json: dict[str, any]) -> ScenarioMarketManagerConfig:
    return ScenarioMarketManagerConfig(
        asset_name=json.get("asset_name", ""),
        adp=int(json.get("adp", 6)),
        mdp=int(json.get("mdp", 6)),
        pdp=int(json.get("pdp", 0)),
    )


def scenario_market_maker_config_from_json(json: dict[str, any]) -> ScenarioMarketMakerConfig:
    isolated_margin_factor = json.get("isolated_margin_factor", None)

    return ScenarioMarketMakerConfig(
        market_kappa=float(json.get("market_kappa", 0.15)),
        market_order_arrival_rate=int(json.get("market_order_arrival_rate", 100)),
        order_kappa=float(json.get("order_kappa", 0.15)),
        order_size=int(json.get("order_size", 1)),
        order_levels=int(json.get("order_levels", 25)),
        order_spacing=float(json.get("order_spacing", 1)),
        order_clipping=int(json.get("order_clipping", 10000)),
        inventory_lower_boundary=int(json.get("inventory_lower_boundary", -3)),
        inventory_upper_boundary=int(json.get("inventory_upper_boundary", 3)),
        fee_amount=float(json.get("fee_amount", 0.0001)),
        commitment_amount=int(json.get("commitment_amount", 800000)),
        initial_mint=int(json.get("initial_mint", 200000)),
        isolated_margin_factor=(None if isolated_margin_factor is None else float(isolated_margin_factor)),
    )


def scenario_auction_trader_config_from_json(json: dict[str, any]) -> ScenarioAuctionTraderConfig:
    return ScenarioAuctionTraderConfig(
        traders=int(json.get("traders", 2)),
        initial_volume=float(json.get("initial_volume", 0.001)),
        initial_mint=int(json.get("initial_mint", 10000)),
    )


def scenario_random_trader_config_from_json(json: dict[str, any]) -> ScenarioRandomTraderConfig:
    return ScenarioRandomTraderConfig(
        traders=int(json.get("traders", 3)),
        order_intensity=[int(val) for val in json.get("order_intensity", [])],
        order_volume=[float(val) for val in json.get("order_volume", [])],
        step_bias=[float(val) for val in json.get("step_bias", [])],
        initial_mint=int(json.get("initial_mint", 1000000)),
    )


def scenario_sensitive_trader_config_from_json(json: dict[str, any]) -> ScenarioSensitiveTraderConfig:
    return ScenarioSensitiveTraderConfig(
        traders=int(json.get("traders", 3)),
        scale=[int(val) for val in json.get("scale", [])],
        max_order_size=[float(val) for val in json.get("max_order_size", [])],
        initial_mint=int(json.get("initial_mint", 10000)),
    )


def scenario_simulation_config_from_json(json: dict[str, any]) -> ScenarioSimulationConfig:
    return ScenarioSimulationConfig(
        n_steps=int(json.get("n_steps", 360)),
        granularity=json.get("granularity", "MINUTE"),
        coinbase_code=json.get("coinbase_code", "BTC-USDT"),
        start_date=json.get("start_date", "2022-11-01 00:00:00"),
        randomise_history=bool(json.get("randomise_history", False)),
    )


def scenario_automated_market_maker_config_from_json(json: dict[str, any]) -> ScenarioAutomatedMarketMaker:
    return ScenarioAutomatedMarketMaker(
        commitment_amount=int(json.get("commitment_amount", 100000)),
        proposed_fee=float(json.get("proposed_fee", 0.0001)),
        lower_bound_scaling=float(json.get("lower_bound_scaling", 0.9)),
        upper_bound_scaling=float(json.get("upper_bound_scaling", 1.1)),
        leverage_at_lower_bound=float(json.get("leverage_at_lower_bound", 20)),
        leverage_at_upper_bound=float(json.get("leverage_at_upper_bound", 20)),
        update_bias=float(json.get("update_bias", 0.001)),
        slippage_tolerance=float(json.get("slippage_tolerance", 0.5)),
        initial_mint=int(json.get("initial_mint", 200000)),
    )


def scenario_config_from_json(json: dict[str, any]) -> ScenarioConfig:
    return ScenarioConfig(
        enable_top_up=bool(json.get("enable_top_up", True)),
        market_name=json.get("market_name", ""),
        market_code=json.get("market_code", ""),
        price_symbol=json.get("price_symbol", ""),
        price_source=json.get("price_source", ""),
        feed_price_multiplier=json.get("feed_price_multiplier", 1),
        step_length_seconds=int(json.get("step_length_seconds", 10)),
        market_manager=scenario_market_manager_config_from_json(json.get("market_manager_args", {})),
        market_maker=scenario_market_maker_config_from_json(json.get("market_maker_args", {})),
        automated_market_maker=scenario_automated_market_maker_config_from_json(
            json.get("automated_market_maker_args", {})
        ),
        auction_trader=scenario_auction_trader_config_from_json(json.get("auction_trader_args", {})),
        random_trader=scenario_random_trader_config_from_json(json.get("random_trader_args", {})),
        sensitive_trader=scenario_sensitive_trader_config_from_json(json.get("sensitive_trader_args", [])),
        simulation=scenario_simulation_config_from_json(json.get("simulation_args", {})),
    )


def wallet_config_from_json(json: dict[str, any]) -> WalletConfig:
    passphrase_file = json.get("passphrase_file", "./assets/passphrase.txt")
    if not os.path.isabs(passphrase_file):
        passphrase_file = os.path.abspath(os.path.join(os.getcwd(), passphrase_file))

    wallet_home = json.get("home", "./wallethome")
    if not os.path.isabs(wallet_home):
        wallet_home = os.path.abspath(os.path.join(os.getcwd(), wallet_home))

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
        wallet_url=json.get("wallet_url", "http://127.0.0.1:1789"),
        tokens_file=json.get("tokens_file", "./network/wallet-info.json"),
        state_file=json.get("state_file", "./network/wallet-state.json"),
    )


def http_server_config_from_json(json: dict[str, any]) -> HttpServerConfig:
    return HttpServerConfig(
        interface=json.get("interface", "0.0.0.0"),
        port=int(json.get("port", 8080)),
    )


def config_from_json(json: dict[str, any]) -> BotsConfig:
    work_dir = json.get("work_dir", "./network")
    if not os.path.isabs(work_dir):
        work_dir = os.path.abspath(os.path.join(os.getcwd(), work_dir))

    wallet_config = wallet_config_from_json(json.get("vegawallet", dict()))

    raw_scenarios_config = json.get("scenario", dict())

    config = BotsConfig(
        network_config_file=json.get("network_config_file", ""),
        debug=bool(json.get("debug", False)),
        work_dir=work_dir,
        wallet=wallet_config,
        http_server=http_server_config_from_json(json.get("http_server", dict())),
        scenarios={
            scenario_name: scenario_config_from_json(raw_scenarios_config[scenario_name])
            for scenario_name in raw_scenarios_config
        },
        devops_network_name=wallet_config.network_name,
        vega_market_sim_network_name=_market_sim_network_from_devops_network_name(wallet_config.network_name),
        network_config=None,
    )

    return config


##
# Network config aka wallet toml config
##
def api_network_config_from_dict(data: dict[str, any]) -> ProtocolAPINetworkConfig:
    retries = data.get("Retries", None)

    return ProtocolAPINetworkConfig(hosts=data.get("Hosts", []), retries=int(retries) if not retries is None else None)


def apps_network_config_from_dict(data: dict[str, any]) -> AppsNetworkConfig:
    return AppsNetworkConfig(
        console=data.get("Console", None), governance=data.get("Governance", None), explorer=data.get("Explorer", None)
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
            for metadata in data.get("Metadata", [])
            if "Key" in metadata and "Value" in metadata
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
            f.write(config_content.decode("utf-8"))

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
        config_json = read_config_from_url(path)
    else:
        config_json = read_config_from_file(path)

    return config_from_json(config_json)
