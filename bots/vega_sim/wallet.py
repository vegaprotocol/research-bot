import bots.config.types

from vega_sim.wallet.vega_wallet import VegaWallet

from typing import Optional
from multiprocessing import Lock

def from_config(config: bots.config.types.WalletConfig, mutex: Optional[Lock]) -> VegaWallet:
    """
    Create the Vegawallet instance implemented by vega-market-sim
    """

    return VegaWallet(
        wallet_url = config.wallet_url,
        wallet_path = config.binary,
        vega_home_dir = config.home,
        passphrase_file_path = config.passphrase_file,
        mutex = mutex,
    )
