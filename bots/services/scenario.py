import logging
import multiprocessing

from bots.services.service import Service
from bots.services.multiprocessing import threaded
from bots.vega_sim.network import network_from_devops_network_name

from vega_sim.scenario.constants import Network
from vega_sim.devops.scenario import DevOpsScenario
from vega_sim.network_service import VegaServiceNetwork

from vega_sim.devops.scenario import DevOpsScenario
from vega_sim.devops.classes import (
    MarketMakerArgs,
    MarketManagerArgs,
    AuctionTraderArgs,
    RandomTraderArgs,
    SensitiveTraderArgs,
    SimulationArgs,
)

from vega_sim.scenario.common.utils.price_process import Granularity

class ScenarioService(Service):
    def __init__(self, name: str, scenario_config: dict[str, any], vega: VegaServiceNetwork, network: str, scenario: DevOpsScenario) -> None:
        self.name = name
        self.vega = vega
        self.scenario_config = scenario_config
        self.network = network
        self.scenario = scenario
        self.logger = logging.getLogger(f"scenario-{name}")

    @threaded
    def start(self):
        self.logger.info("Starting scenario")
        self.scenario.market_name = self.scenario_config.get("market_name", "missing-market-name")
        self.scenario.step_length_seconds = self.scenario_config.get("step_length_seconds", 10)
        self.scenario.run_iteration(
            vega=self.vega,
            network=Network[self.network],
            pause_at_completion=False,
            raise_datanode_errors=False,
            raise_step_errors=False,
            run_with_snitch=False,
        )


def services_from_config(vega_sim_network_name: str, scenarios_config: dict[str, any], network_config_path: str, wallet_binary: str, wallet_mutex: multiprocessing.Lock) -> list[Service]:
    if scenarios_config is None or len(scenarios_config) < 1:
        raise ValueError("Cannot create services because scenarios are none")
    
    scenarios = _scenarios_from_config(scenarios_config)

    services = []

    for scenario_name in scenarios:
        services.append(ScenarioService(
            scenario_name, 
            scenarios_config[scenario_name], 
            network_from_devops_network_name(vega_sim_network_name, network_config_path, wallet_binary, wallet_mutex), 
            vega_sim_network_name, 
            scenarios[scenario_name]))

    return services


def _scenarios_from_config(config: dict[str, dict[str, any]]) -> dict[str, DevOpsScenario]:
    result = {}

    for scenario_name in config:
        market_manager_args = config[scenario_name].get("market_manager_args", {})
        market_maker_args = config[scenario_name].get("market_maker_args", {})
        auction_trader_args = config[scenario_name].get("auction_trader_args", {})
        random_trader_args = config[scenario_name].get("random_trader_args", {})
        sensitive_trader_args = config[scenario_name].get("sensitive_trader_args", {})
        simulation_args = config[scenario_name].get("simulation_args", {})

        missing = lambda key: f"missing-{key}-for-{scenario_name}"


        result.update({f"{scenario_name}": DevOpsScenario(
            binance_code=config[scenario_name].get("biance_code", missing("biance-code")),
            market_manager_args=MarketManagerArgs(
                market_name=str(market_manager_args.get("market_name", missing("market-name"))),
                market_code=str(market_manager_args.get("market_name", missing("market-code"))),
                asset_name=str(market_manager_args.get("asset_name", missing("asset-name"))),
                adp=int(market_manager_args.get("adp", missing("adp"))),
                mdp=int(market_manager_args.get("mdp", missing("mdp"))),
                pdp=int(market_manager_args.get("pdp", missing("pdp"))),
            ),
            market_maker_args=MarketMakerArgs(
                market_kappa=float(market_maker_args.get("market_kappa", missing("market_kappa"))),
                market_order_arrival_rate=int(market_maker_args.get("market_order_arrival_rate", missing("market_order_arrival_rate"))),
                order_kappa=float(market_maker_args.get("order_kappa", missing("order_kappa"))),
                order_size=int(market_maker_args.get("order_size", missing("order_size"))),
                order_levels=int(market_maker_args.get("order_levels", missing("order_levels"))),
                order_spacing=float(market_maker_args.get("order_spacing", missing("order_spacing"))),
                order_clipping=int(market_maker_args.get("order_clipping", missing("order_clipping"))),
                inventory_lower_boundary=int(market_maker_args.get("inventory_lower_boundary", missing("inventory_lower_boundary"))),
                inventory_upper_boundary=int(market_maker_args.get("inventory_upper_boundary", missing("inventory_upper_boundary"))),
                fee_amount=float(market_maker_args.get("fee_amount", missing("fee_amount"))),
                commitment_amount=int(market_maker_args.get("commitment_amount", missing("commitment_amount"))),
                initial_mint=int(market_maker_args.get("initial_mint", missing("initial_mint"))),
            ),
            auction_trader_args=AuctionTraderArgs(
                initial_volume=float(auction_trader_args.get("initial_volume", missing("initial_volume"))),
                initial_mint=int(auction_trader_args.get("initial_mint", missing("initial_mint"))),
            ),
            random_trader_args=RandomTraderArgs(
                order_intensity=[int(val) for val in random_trader_args.get("order_intensity", [])],
                order_volume=[float(val) for val in random_trader_args.get("order_volume", [])],
                step_bias=[float(val) for val in random_trader_args.get("step_bias", [])],
                initial_mint=int(random_trader_args.get("initial_mint", missing("initial_mint"))),
            ),
            sensitive_trader_args=SensitiveTraderArgs(
                scale=[int(val) for val in sensitive_trader_args.get("scale", [])],
                max_order_size=[float(val) for val in sensitive_trader_args.get("max_order_size", [])],
                initial_mint=int(sensitive_trader_args.get("initial_mint", missing("initial_mint"))),
            ),
            simulation_args=SimulationArgs(
                n_steps=int(simulation_args.get("n_steps", missing("n_steps"))),
                granularity=_dispatch_granularity(simulation_args.get("granularity", "MINUTE")),
                coinbase_code=str(simulation_args.get("coinbase_code", missing("coinbase_code"))),
                start_date=str(simulation_args.get("start_date", missing("start_date"))),
                randomise_history=_dispatch_bool(simulation_args.get("randomise_history", False)),
            ),
        )
    })

    return result

def _dispatch_bool(val: str) -> bool:
    if isinstance(val, bool):
        return val
    
    return val.lower() in ["true", "t", "on"]

def _dispatch_granularity(val: str) -> Granularity:
    if val == "MINUTE":
        return Granularity.MINUTE
    elif val == "FIVE_MINUTE":
        return Granularity.FIVE_MINUTE
    elif val == "FIFTEEN_MINUTE":
        return Granularity.FIFTEEN_MINUTE
    elif val == "HOUR":
        return Granularity.HOUR
    elif val == "SIX_HOUR":
        return Granularity.SIX_HOUR
    elif val == "DAY":
        return Granularity.DAY
    else:
        return int(val)

