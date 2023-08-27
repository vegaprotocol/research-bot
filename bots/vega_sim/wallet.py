from vega_sim.wallet import VegaWallet

from typing import Optional
from multiprocessing import Lock

def from_config(config: dict[str, str], binary_path_override: str, mutex: Optional[Lock]) -> VegaWallet:
    """
    Create the Vegawallet instance implemented by vega-market-sim
    """

    binary_path = config.get()

    return VegaWallet(
        wallet_path = config[]
    )

        config.get("network", "mainnet-mirror"),
        config.get("passphrase_file"),
        config.get("home"),
        config.get("wallet_name")
    

    
        # self,
        # wallet_url: str,
        # wallet_path: str | list[str],
        # vega_home_dir: str,
        # passphrase_file_path: Optional[str] = None,
        # mutex: Optional[multiprocessing.Lock] = None,