import logging
import subprocess


import bots.config.types
from bots.services.service import Service
from bots.services.multiprocessing import threaded


class VegaWalletService(Service):
    """
    Start and run the vega wallet process
    """

    default_bin_path = "VegaWalletService"
    logger = logging.getLogger("VegaWalletService")

    def __init__(
        self, bin_path: str | list[str], network_name: str, passphrase_file: str, wallet_home: str, wallet_name: str
    ) -> None:
        if isinstance(bin_path, str):
            self.bin_path = [bin_path]
        else:
            self.bin_path = bin_path
        if bin_path is None:
            self.bin_path = VegaWalletService.default_bin_path

        self.passphrase_file = passphrase_file
        self.network_name = network_name
        self.wallet_home = wallet_home
        self.wallet_name = wallet_name

        self.process = None
        self.process_thread = None

    def wait(self):
        pass

    def check(self):
        from shutil import which
        from os.path import isdir, exists

        wallet_binary = self.bin_path
        if not isinstance(self.bin_path, str):
            wallet_binary = self.bin_path[0]

        if which(wallet_binary) is None:
            raise Exception("Wallet binary not found")

        if not self.wallet_home is None and not isdir(self.wallet_home):
            raise Exception("Wallet home does not exists")

        if self.network_name is None:
            raise Exception("Network name is none")

        if self.passphrase_file is None:
            raise Exception("Passphrase file is none")

        if not exists(self.passphrase_file):
            raise Exception("Passphrase file does not exists")

        if self.wallet_name is None:
            raise Exception("Wallet name cannot be None for check function")

        # add check for free port

        # wallet_args = self._wallet_args(["wallet", "key", "list", "--wallet", self.wallet_name])
        # print(wallet_args)
        # process = subprocess.Popen(wallet_args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # process.wait()
        # if process.poll() != 0:
        #     out, err = process.communicate()
        #     raise Exception(f"The {self.wallet_name} wallet does not exist in the VegaWalletService. Stdout: {out}, Stderr: {err}")

    def _wallet_args(self, command: list[str], with_network: bool = False) -> list[str]:
        wallet_args = self.bin_path + command
        if with_network:
            wallet_args = wallet_args + [
                "--network",
                self.network_name,
                "--load-tokens",
                "--automatic-consent",
                "--tokens-passphrase-file",
                self.passphrase_file,
            ]
        else:
            wallet_args = wallet_args + [
                "--passphrase-file",
                self.passphrase_file,
            ]

        if not self.wallet_home is None:
            wallet_args = wallet_args + ["--home", self.wallet_home]

        return wallet_args

    def run(self, check: bool = False) -> subprocess.CompletedProcess:
        """
        Starts the VegaWalletService binary for the given network
        """
        VegaWalletService.logger.info("Starting the VegaWalletService process")
        if self.process != None:
            raise RuntimeError("Wallet is already running")

        wallet_args = self._wallet_args(["wallet", "service", "run"], True) + ["--no-version-check"]

        self.process = subprocess.Popen(
            wallet_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        try:
            with self.process.stdout:
                for line in iter(self.process.stdout.readline, b""):
                    VegaWalletService.logger.debug(line.decode("utf-8").strip())

        except subprocess.CalledProcessError as e:
            VegaWalletService.logger.error(f"{str(e)}")

        retcode = self.process.poll()
        if check and retcode:
            raise subprocess.CalledProcessError(retcode, self.process.args)
        return subprocess.CompletedProcess(self.process.args, retcode)

    @threaded
    def start(self):
        VegaWalletService.logger.info("Running the wallet in the background")
        self.run(check=True)

    def __del__(self):
        """
        Manage the resource reserved by this class
        """
        VegaWalletService.logger.info("Stopping the VegaWalletService process")
        if not self.process is None:
            self.process.kill()
            VegaWalletService.logger.info("Stopped the VegaWalletService process")


def from_config(config: bots.config.types.WalletConfig) -> VegaWalletService:
    VegaWalletService.logger.info(f"Vegawallet will start with binary: {config.binary}")

    return VegaWalletService(
        bin_path=config.binary,
        network_name=config.network_name,
        passphrase_file=config.passphrase_file,
        wallet_home=config.home,
        wallet_name=config.wallet_name,
    )
