import logging
import argparse

from bots.services.multiprocessing import service_manager
from bots.services.healthcheck import HealthCheckService
from bots.services.vega_wallet import VegaWalletService
from bots.config.config import read_config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-c", "--config", default="./config.toml")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    config = read_config(args.config)

    vegawallet_config = config["vegawallet"]
    processes = service_manager([
        HealthCheckService(host="0.0.0.0", port=8080),
        VegaWalletService(
            vegawallet_config.get("binary"), 
            vegawallet_config.get("network", "mainnet-mirror"), 
            vegawallet_config.get("passphrase_file"), 
            vegawallet_config.get("home"), 
            vegawallet_config.get("wallet_name")
        ),
        
    ])


   

if __name__ == "__main__":
    main()
