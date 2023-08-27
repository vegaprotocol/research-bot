import os
import logging
import os.path
import signal
import argparse
import multiprocessing

from bots.services.multiprocessing import service_manager
from bots.services.scenario import services_from_config
from bots.services.healthcheck import from_config as healthcheck_from_config
from bots.services.traders import from_config as traders_from_config
from bots.services.vega_wallet import from_config as wallet_from_config
from bots.config.environment import check_env_variables
from bots.api.datanode import check_market_exists, get_statistics
from bots.tools.github import download_and_unzip_github_asset
from bots.config.network import load_network_config
from bots.config.config import read_config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="./config.toml")
    args = parser.parse_args()

    config = read_config(args.config)
    logging.basicConfig(level=logging.DEBUG if bool(config.get("debug", False)) else logging.INFO)
    network_config = load_network_config(config.network_config_file, config.devops_network_name, config.work_dir)

    rest_api_endpoints = network_config.api.rest.hosts
    required_market_names = [scenarios_config[scenario_name]["market_name"] for scenario_name in scenarios_config]
    statistics = get_statistics(rest_api_endpoints)

    try:
        if config.wallet.download_wallet_binary:
            binary_path = download_and_unzip_github_asset(
                config.wallet.artifact_name, 
                statistics["appVersion"] if config.wallet.auto_version else config.wallet.version,
                config.work_dir,
                config.wallet.repository,
            )
            # We uses vegawallet from the vega binary
            if config.wallet.artifact_name == "vega":
                binary_path = [binary_path, "wallet"]

            config.wallet.update_binary(binary_path)
    except Exception as e:
        return


    scenarios_config = dict() if "scenario" not in config else config["scenario"]
    try:
        check_env_variables()
        check_market_exists(rest_api_endpoints, required_market_names)
    except Exception as e:
        logging.error(str(e))
        return
    
    services = [
        healthcheck_from_config(config.http_server),
        traders_from_config(config.http_server),
        wallet_from_config(config.wallet),
    ]

    wallet_mutex = multiprocessing.Lock()
    services += services_from_config(
        config.vega_market_sim_network_name, 
        scenarios_config, 
        os.path.dirname(network_config.file_path), 
        config.wallet.binary, 
        wallet_mutex
    )

    processes = service_manager(services)
    signal.sigwait([signal.SIGINT, signal.SIGKILL,signal.SIGABRT, signal.SIGTERM, signal.SIGQUIT])
    logging.info("Program received stop signal")

    for process in processes:
        process.kill()
    

   

if __name__ == "__main__":
    main()
