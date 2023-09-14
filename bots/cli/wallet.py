import bots.config.types
import subprocess


# @$(WALLET_BIN) api-token generate \
#         --description "vegamarketsim" \
#         --home $(VEGA_WALLET_HOME) \
#         --wallet-name vegamarketsim \
#         --wallet-passphrase-file $(VEGA_WALLET_TOKENS_PASSPHRASE_FILE) \
#         --tokens-passphrase-file $(VEGA_WALLET_TOKENS_PASSPHRASE_FILE) \
#         --output=json > $(BOTS_WORKING_DIR)/api-token-generate.json

def generate_wallet_token(wallet_name: str, wallet_config: bots.config.types.WalletConfig) -> str:
    args = [
        wallet_config.binary,
        "--description", wallet_name,
        "--wallet-name", wallet_name,
        "--wallet-passphrase-file", wallet_config.passphrase_file,
        "--tokens-passphrase-file", wallet_config.passphrase_file,
        "--output=json"
    ]

    if len(wallet_config.home) > 0:
        args = args + [
            "--home", wallet_config.home,
        ]

    with subprocess.Popen(args, stdout=subprocess.PIPE) as proc:
        print(proc.stdout.read())


def list_keys_for_wallet(wallet_name: str, wallet_config: bots.config.types.WalletConfig):
    pass

def create_key(wallet_name: str, key_name: str, wallet_config: bots.config.types.WalletConfig): 
    pass

def create_wallet(wallet_name: str, wallet_config: bots.config.types.WalletConfig):
    pass