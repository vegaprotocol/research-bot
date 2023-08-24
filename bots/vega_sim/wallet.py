from vega_sim.wallet import VegaWallet

from typing import Optional
from multiprocessing import Lock

def from_config(config: dict[str, str], mutex: Optional[Lock]) -> VegaWallet:
    return VegaWallet(
       
    )

      config.get("network", "mainnet-mirror"),
        config.get("passphrase_file"),
        config.get("home"),
        config.get("wallet_name")
    

    # def __init__(
    #     self,
    #     wallet_url: str,
    #     wallet_path: str,
    #     vega_home_dir: str,
    #     passphrase_file_path: Optional[str] = None,
    #     mutex: Optional[multiprocessing.Lock] = None,
    # ):