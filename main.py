import os
import logging
import os.path
import signal
import argparse
import multiprocessing

from bots.services.multiprocessing import service_manager
from bots.services.scenario import services_from_config
from bots.services.healthcheck import from_config as healthcheck_from_config
from bots.services.vega_wallet import from_config as wallet_from_config
from bots.config.config import read_config, local_network_config_path, load_network_config_file
from bots.config.environment import check_env_variables
from bots.api.core import check_market_exists
from bots.vega_sim.network import market_sim_network_from_devops_network_name
from bots.tools.github import download_and_unzip_github_asset


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-c", "--config", default="./config.toml")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    base_path = os.path.abspath("./network")

    config = read_config(args.config)
    scenarios_config = dict() if "scenario" not in config else config["scenario"]
    vegawallet_config = config["vegawallet"]
    wallet_binary = vegawallet_config.get("binary")
    devops_network_name = vegawallet_config.get("network", "mainnet-mirror")
    market_sim_network_name = market_sim_network_from_devops_network_name(devops_network_name)

    network_config_path = local_network_config_path(config.get("network_config_file"), devops_network_name, base_path)
    network_config = load_network_config_file(network_config_path)

    rest_api_endpoints = network_config["API"]["REST"]["Hosts"]
    required_market_names = [scenarios_config[scenario_name]["market_name"] for scenario_name in scenarios_config]

    vegawallet_binary_override = None
    try:
        check_env_variables()
        check_market_exists(rest_api_endpoints, required_market_names)
        if bool(vegawallet_config.get("download_wallet_binary", False)):
            vegawallet_binary_override = download_and_unzip_github_asset(
                "vegawallet", 
                vegawallet_config.get("version"),
                base_path,
                vegawallet_config.get("repository")
            )
    except Exception as e:
        logging.error(str(e))
        return
    
    services = [
        healthcheck_from_config(config.get("healthcheck", dict())),
        wallet_from_config(vegawallet_config, vegawallet_binary_override),
    ]
    

    wallet_mutex = multiprocessing.Lock()
    services += services_from_config(market_sim_network_name, scenarios_config, os.path.dirname(network_config_path), wallet_binary, wallet_mutex)

    processes = service_manager(services)
    catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
    for sig in catchable_sigs:
        signal.signal(sig, print)
    signal.sigwait([signal.SIGINT, signal.SIGKILL,signal.SIGABRT, signal.SIGTERM, signal.SIGQUIT])
    logging.info("Program received stop signal")

    for process in processes:
        process.kill()
    

   

if __name__ == "__main__":
    main()
