import bots.config.types
import logging

from vega_sim.devops.wallet import ScenarioWallet, Agent
from bots.wallet.cli import VegaWalletCli


def from_config(
    scenarios_config: bots.config.types.ScenariosConfigType, wallet_cli: VegaWalletCli
) -> dict[str, ScenarioWallet]:
    result = dict()
    for scenario_name in scenarios_config:
        result.update(
            {
                f"{scenario_name}": ScenarioWallet(
                    market_creator_agent=Agent(key_name=f"market_creator", wallet_name=scenario_name),
                    market_settler_agent=Agent(key_name=f"market_settler", wallet_name=scenario_name),
                    market_maker_agent=Agent(key_name=f"market_maker", wallet_name=scenario_name),
                    auction_trader_agents=[
                        Agent(key_name=f"auction_trader_{trader}", wallet_name=scenario_name)
                        for trader in range(scenarios_config[scenario_name].auction_trader.traders)
                    ],
                    random_trader_agents=[
                        Agent(key_name=f"random_trader_{trader}", wallet_name=scenario_name)
                        for trader in range(scenarios_config[scenario_name].random_trader.traders)
                    ],
                    sensitive_trader_agents=[
                        Agent(key_name=f"sensitive_trader_{trader}", wallet_name=scenario_name)
                        for trader in range(scenarios_config[scenario_name].sensitive_trader.traders)
                    ],
                )
            }
        )

    # Make sure proper wallets exist
    for scenario_name in result:
        scenario_wallet = result[scenario_name]

        wallet_name = scenario_wallet.market_creator_agent.wallet_name

        wallet_keys = {}

        if not wallet_cli.wallet_exists(wallet_name):
            logging.info(f"Creating the {scenario_wallet.market_creator_agent.wallet_name} wallet")
            wallet_cli.create_wallet(wallet_name)
            wallet_cli.generate_api_token(wallet_name)
            existing_key_pairs = dict()
        else:
            wallet_keys = wallet_cli.list_keys(wallet_name)

        if not scenario_wallet.market_creator_agent.key_name in wallet_keys:
            logging.info(
                f"Creating the {scenario_wallet.market_creator_agent.key_name} key pair in the {scenario_wallet.market_creator_agent.wallet_name} wallet"
            )
            wallet_cli.generate_key(
                scenario_wallet.market_creator_agent.wallet_name, scenario_wallet.market_creator_agent.key_name
            )

        if not scenario_wallet.market_settler_agent.key_name in wallet_keys:
            logging.info(
                f"Creating the {scenario_wallet.market_settler_agent.key_name} key pair in the {scenario_wallet.market_settler_agent.wallet_name} wallet"
            )
            wallet_cli.generate_key(
                scenario_wallet.market_settler_agent.wallet_name, scenario_wallet.market_settler_agent.key_name
            )

        if not scenario_wallet.market_maker_agent.key_name in wallet_keys:
            logging.info(
                f"Creating the {scenario_wallet.market_maker_agent.key_name} key pair in the {scenario_wallet.market_maker_agent.wallet_name} wallet"
            )
            wallet_cli.generate_key(
                scenario_wallet.market_maker_agent.wallet_name, scenario_wallet.market_maker_agent.key_name
            )

        for agent in scenario_wallet.auction_trader_agents:
            if not agent.key_name in wallet_keys:
                logging.info(f"Creating the {agent.key_name} key pair in the {agent.wallet_name} wallet")
                wallet_cli.generate_key(agent.wallet_name, agent.key_name)

        for agent in scenario_wallet.random_trader_agents:
            if not agent.key_name in wallet_keys:
                logging.info(f"Creating the {agent.key_name} key pair in the {agent.wallet_name} wallet")
                wallet_cli.generate_key(agent.wallet_name, agent.key_name)

        for agent in scenario_wallet.sensitive_trader_agents:
            if not agent.key_name in wallet_keys:
                logging.info(f"Creating the {agent.key_name} key pair in the {agent.wallet_name} wallet")
                wallet_cli.generate_key(agent.wallet_name, agent.key_name)

    return result
