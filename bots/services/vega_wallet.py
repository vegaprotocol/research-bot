import logging
import subprocess
from bots.services.multiprocessing import threaded


class VegaWalletService:
    """
    Start and run the vega wallet process
    """
    default_bin_path = "VegaWalletService"
    logger = logging.getLogger("VegaWalletService")

    def __init__(self, bin_path: str, network_name: str, token_file_path: str, wallet_home: str) -> None:
        self.bin_path = bin_path
        if bin_path is None:
            self.bin_path = VegaWalletService.default_bin_path
        
        self.token_file_path = token_file_path
        self.network_name = network_name
        self.wallet_home = wallet_home

        self.process = None
        self.process_thread = None
    
    def check_wallet(self, wallet_name: str):
        from shutil import which
        from os.path import isdir, exists
        
        if which(self.bin_path) is None:
            raise Exception("Wallet binary not found")
        
        if not self.wallet_home is None and not isdir(self.wallet_home):
            raise Exception("Wallet home does not exists")
        
        if self.network_name is None:
            raise Exception('Network name is none')
        
        if self.token_file_path is None:
            raise Exception('Passphrase file is none')
        
        if not exists(self.token_file_path):
            raise Exception('Passphrase file does not exists')
        
        if wallet_name is None:
            raise Exception('Wallet name cannot be None for check function')
        
        wallet_args = self._wallet_args(("key", "list", "--wallet", wallet_name))
        print(wallet_args)
        process = subprocess.Popen(wallet_args, shell=True, stdout=subprocess.PIPE)
        process.wait()
        if process.poll() != 0:
            raise Exception(f"The {wallet_name} wallet does not exist in the VegaWalletService")


    def _wallet_args(self, command: tuple) -> tuple:
        wallet_args = (
            self.bin_path,
        )
        wallet_args = wallet_args + command
        wallet_args = wallet_args + (
            "service",
            "run",
            "--network",
            self.network_name,
            "--load-tokens",
            "--automatic-consent",
            "--tokens-passphrase-file",
            self.token_file_path,
        )
        
        if not self.wallet_home is None:
            wallet_args = wallet_args + ("--home", self.wallet_home, )
        
        return wallet_args


    def run(self, check: bool = False) -> subprocess.CompletedProcess:
        """
        Starts the VegaWalletService binary for the given network
        """
        VegaWalletService.logger.info("Starting the VegaWalletService process")
        if self.process != None:
            raise RuntimeError("Wallet is already running")
        
        wallet_args = self._wallet_args(("service", "run")) + ("--no-version-check", )

        self.process = subprocess.Popen(
            wallet_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        try:
            with self.process.stdout:
                for line in iter(self.process.stdout.readline, b''):
                    VegaWalletService.logger.info(line.decode("utf-8").strip())
                
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
            