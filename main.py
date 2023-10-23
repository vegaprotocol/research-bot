import os
import logging
import argparse
import bots.http.app

from bots.services.multiprocessing import service_manager
from bots.services.scenario import services_from_config
from bots.http.traders_handler import from_config as traders_from_config
from bots.services.vega_wallet import from_config as wallet_from_config
from bots.vega_sim.scenario_wallet import from_config as scenario_wallet_from_config
from bots.config.environment import check_env_variables
from bots.api.datanode import check_market_exists, get_statistics
from bots.tools.github import download_and_unzip_github_asset
from bots.config.types import load_network_config, read_bots_config
from bots.wallet.cli import VegaWalletCli


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="./research-bots-config-stagnet1.toml")
    args = parser.parse_args()
    tokens = os.getenv("TOKENS", "")
    tokens_list = [token.strip() for token in tokens.split(",") if len(token.strip()) > 1]

    config = read_bots_config(args.config)
    logging.basicConfig(level=logging.DEBUG if config.debug else logging.INFO)
    config.update_network_config(
        load_network_config(config.network_config_file, config.devops_network_name, config.work_dir)
    )
    bots.http.app.configure_flask(config.debug)

    scenarios_config = config.scenarios

    rest_api_endpoints = config.network_config.api.rest.hosts
    required_market_names = [scenarios_config[scenario_name].market_name for scenario_name in scenarios_config]
    statistics = get_statistics(rest_api_endpoints)

    wallet_mutex = None

    try:
        if config.wallet.download_wallet_binary:
            binary_path = download_and_unzip_github_asset(
                config.wallet.artifact_name,
                statistics["appVersion"] if config.wallet.auto_version else config.wallet.version,
                config.work_dir,
                config.wallet.repository,
            )

            # update custom branch
            config.wallet.update_binary(binary_path)
    except Exception as e:
        logging.error(str(e))
        return
    

    # before the wallet http server is started we need to use the CLI
    cli_wallet = VegaWalletCli(config.wallet)
    if not cli_wallet.is_initialized():
        cli_wallet.init()
        cli_wallet.import_internal_networks()



    # before the wallet http server is started we need to use the CLI
    cli_wallet = VegaWalletCli(config.wallet)
    if not cli_wallet.is_initialized():
        cli_wallet.init()
        cli_wallet.import_internal_networks()


    scenario_wallets = dict()
    try:
        check_env_variables()
        check_market_exists(rest_api_endpoints, required_market_names)
        scenario_wallets = scenario_wallet_from_config(config.scenarios, cli_wallet)
        traders_svc = traders_from_config(config, cli_wallet, scenario_wallets, tokens_list)
        bots.http.app.handler(path="/traders", handler_func=lambda: traders_svc.serve())
    except Exception as e:
        logging.error(str(e))
        return

    services = [
        wallet_from_config(config.wallet),
    ]

    services += services_from_config(
        config.vega_market_sim_network_name,
        scenario_wallets,
        scenarios_config,
        os.path.dirname(config.network_config.file_path),
        config.wallet,
        wallet_mutex,
    )

    processes = service_manager(services)

    try:
        bots.http.app.run(config.debug, config.http_server)
    except Exception as e:
        logging.error("HTTP Server failed with error: " + str(e))

    # for process in processes:
    #     process.kill()


if __name__ == "__main__":
    with_pprof = os.getenv("WITH_PPROF", "")
    if with_pprof != "":
        logging.info("Starting pprof server on port 8081")
        from pypprof.net_http import start_pprof_server
        start_pprof_server(port=8081)
    main()