import logging
from vega_sim.network_service import VegaServiceNetwork
from vega_sim.scenario.constants import Network

logger = logging.getLogger("vega-sim")


def market_sim_network_from_devops_network_name(net_name: str) -> str:
    mapping = {
        "devnet1": "DEVNET1",
        "stagnet1": "STAGNET1",
        "fairground": "FAIRGROUND",
        "mainnet-mirror": "MAINNET_MIRROR",
        "mainnet_mirror": "MAINNET_MIRROR"
    }

    return mapping[net_name]

def network_from_devops_network_name(name: str, network_config_path: str, wallet_token_path: str) -> VegaServiceNetwork:
    market_sim_network_name = market_sim_network_from_devops_network_name(name)
    logger.info("Creating the vega network service")
    return VegaServiceNetwork(
        network=Network[market_sim_network_name],
        run_with_console=False,
        run_with_wallet=False,
        governance_symbol = "VEGA",
        network_config_path = network_config_path,
        wallet_token_path = wallet_token_path,
    )
