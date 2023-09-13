WALLET_BIN=vegawallet
CURRENT_WORKING_DIR=$(shell pwd)
WALLET_PASSPHRASE=123456789

CONFIG_FILE ?= "config.toml"

export BOTS_WORKING_DIR=$(CURRENT_WORKING_DIR)/network
export PREGENERATED_WALLET_PATH=$(CURRENT_WORKING_DIR)/assets/wallets/vegamarketsim 
export VEGA_WALLET_HOME=$(CURRENT_WORKING_DIR)/wallethome
export VEGA_WALLET_TOKENS_FILE=$(BOTS_WORKING_DIR)/wallet-info.json
export VEGA_WALLET_TOKENS_PASSPHRASE_FILE=$(CURRENT_WORKING_DIR)/assets/passphrase.txt


export VEGA_USER_WALLET_NAME=vegamarketsim

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


	@echo "Initializing the wallet";
	@$(WALLET_BIN) init --home $(VEGA_WALLET_HOME) > /dev/null

	@echo "Loading pre-generated wallets into $(VEGA_WALLET_HOME)";
	@cp $(PREGENERATED_WALLET_PATH) $(VEGA_WALLET_HOME)/data/wallets/ 

	@echo "Listening the wallets";
	@$(WALLET_BIN) key list \
			--wallet vegamarketsim \
			--home $(VEGA_WALLET_HOME) \
			--output json \
			--passphrase-file $(VEGA_WALLET_TOKENS_PASSPHRASE_FILE) \
		| jq '.keys' > $(BOTS_WORKING_DIR)/ket-list.json

	@echo "Initializing the API TOKEN";
	@$(WALLET_BIN) api-token init \
	 		--home $(VEGA_WALLET_HOME) \
	 		--output=json \
	 		--passphrase-file $(VEGA_WALLET_TOKENS_PASSPHRASE_FILE) > $(BOTS_WORKING_DIR)/api-token-init.json
	
	@echo "Generating the API TOKEN";
	@$(WALLET_BIN) api-token generate \
			--description "vegamarketsim" \
			--home $(VEGA_WALLET_HOME) \
			--wallet-name vegamarketsim \
			--wallet-passphrase-file $(VEGA_WALLET_TOKENS_PASSPHRASE_FILE) \
			--tokens-passphrase-file $(VEGA_WALLET_TOKENS_PASSPHRASE_FILE) \
			--output=json > $(BOTS_WORKING_DIR)/api-token-generate.json

# We must split step into to in order to reflect file system changes
prepare_wallet: init_wallet
	@echo "Saving the generated token into $(VEGA_WALLET_TOKENS_FILE)";
	@( \
		WALLET_TOKEN=$(shell jq -r '.token' "${BOTS_WORKING_DIR}/api-token-generate.json"); \
		echo "{\"$(VEGA_USER_WALLET_NAME)\": \"$${WALLET_TOKEN}\"}" > $(VEGA_WALLET_TOKENS_FILE) \
	)
	

	@echo "Importing stagnet1 wallet config";
	@$(WALLET_BIN) network import \
			--home $(VEGA_WALLET_HOME) \
			--from-url "https://raw.githubusercontent.com/vegaprotocol/networks-internal/main/stagnet1/vegawallet-stagnet1.toml" \
	> /dev/null


	@echo "Importing vegawallet wallet config";
	@$(WALLET_BIN) network import \
			--home $(VEGA_WALLET_HOME) \
			--from-url "https://raw.githubusercontent.com/vegaprotocol/networks-internal/main/mainnet-mirror/vegawallet-mainnet-mirror.toml" \
	> /dev/null


	@echo "Importing fairground wallet config";
	@$(WALLET_BIN) network import \
			--home $(VEGA_WALLET_HOME) \
			--from-url "https://raw.githubusercontent.com/vegaprotocol/networks-internal/main/fairground/vegawallet-fairground.toml" \
	> /dev/null


	@echo "Importing devnet1 wallet config";
	@$(WALLET_BIN) network import \
			--home $(VEGA_WALLET_HOME) \
			--from-url "https://raw.githubusercontent.com/vegaprotocol/networks-internal/main/devnet1/vegawallet-devnet1.toml" \
	> /dev/null

prepare_bots:
	@poetry install

prepare_bots_prod:
	@poetry install --no-dev

run_bots: prepare_bots
	poetry run python main.py --config "$(CONFIG_FILE)"
