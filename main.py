import os
import logging
import time
import os.path
import signal
import argparse
import multiprocessing
import bots.http.app

from bots.services.multiprocessing import service_manager
from bots.services.scenario import services_from_config
from bots.http.traders_handler import from_config as traders_from_config
from bots.services.vega_wallet import from_config as wallet_from_config
from bots.config.environment import check_env_variables
from bots.api.datanode import check_market_exists, get_statistics
from bots.tools.github import download_and_unzip_github_asset
from bots.config.types import load_network_config, read_bots_config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="./config.toml")
    args = parser.parse_args()

    config = read_bots_config(args.config)
    logging.basicConfig(level=logging.DEBUG if config.debug else logging.INFO)
    config.update_network_config(load_network_config(config.network_config_file, config.devops_network_name, config.work_dir))
    bots.http.app.configure_flask(config.debug)


    wallet_mutex = multiprocessing.Lock()
    traders_svc = traders_from_config(config, wallet_mutex)
    bots.http.app.handler(path="/traders", handler_func=lambda: traders_svc.serve())

    scenarios_config = config.scenarios

    rest_api_endpoints = config.network_config.api.rest.hosts
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
        logging.error(str(e))
        return

    try:
        check_env_variables()
        check_market_exists(rest_api_endpoints, required_market_names)
    except Exception as e:
        logging.error(str(e))
        return
    
    services = [
        wallet_from_config(config.wallet),
    ]

    services += services_from_config(
        config.vega_market_sim_network_name, 
        scenarios_config, 
        os.path.dirname(config.network_config.file_path), 
        config.wallet.binary, 
        wallet_mutex
    )

    processes = service_manager(services)

    bots.http.app.app.run()

    for process in processes:
        process.kill()
    

   

if __name__ == "__main__":
    main()
