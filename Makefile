WALLET_BIN=vegawallet
WORKING_DIR ?= $(shell pwd)
WALLET_PASSPHRASE=123456789

CONFIG_FILE ?= "config.toml"
MEMRAY_ARGS = ""

export BOTS_WORKING_DIR=$(WORKING_DIR)/network
export PREGENERATED_WALLET_PATH=$(WORKING_DIR)/assets/wallets/vegamarketsim 
export VEGA_WALLET_HOME=$(WORKING_DIR)/wallethome
export VEGA_WALLET_TOKENS_FILE ?= $(BOTS_WORKING_DIR)/wallet-info.json
export VEGA_WALLET_TOKENS_PASSPHRASE_FILE=$(WORKING_DIR)/assets/passphrase.txt
# export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

export VEGA_USER_WALLET_NAME=vegamarketsim


black:
	@black --line-length 120 --target-version py311 ./bots
	@black --line-length 120 --target-version py311 ./main.py

blackcheck:
	@black --line-length 120 --target-version py311 --check .


check:
	@if ! $(WALLET_BIN) software version > /dev/null; then \
		echo "Wallet binary is not callable, add $(WALLET_BIN) folder to your PATH"; \
		exit 1; \
	fi;
	@echo "Vegawallet binary looks good";


init_wallet: check
	@echo "Cleaningup the local files";
	@rm -rf $(VEGA_WALLET_HOME);
	@rm -rf $(BOTS_WORKING_DIR);
	@mkdir -p $(VEGA_WALLET_HOME);
	@mkdir -p $(BOTS_WORKING_DIR);

prepare_wallet: init_wallet
	@echo "Pass"

prepare_bots:
	@poetry install

prepare_bots_prod:
	@poetry install --no-dev

run_bots: prepare_bots
	poetry run python main.py --config "$(CONFIG_FILE)"

run_bots_with_pprof: prepare_bots
	WITH_PPROF=1 poetry run python main.py --config "$(CONFIG_FILE)"