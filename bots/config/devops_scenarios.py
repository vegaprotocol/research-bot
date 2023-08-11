from vega_sim.devops.scenario import DevOpsScenario
from vega_sim.devops.classes import (
    MarketMakerArgs,
    MarketManagerArgs,
    AuctionTraderArgs,
    RandomTraderArgs,
    SensitiveTraderArgs,
    SimulationArgs,
)

from vega_sim.scenario.common.utils.price_process import Granularity, LivePrice


def generate_scenario_from_config(config: dict[str, dict[str, any]]) -> dict[str, lambda: DevOpsScenario]:
    result = {}

    for scenario_name in config:
        market_manager_args = config[scenario_name].get("market_manager_args", {})
        market_maker_args = config[scenario_name].get("market_maker_args", {})
        auction_trader_args = config[scenario_name].get("auction_trader_args", {})
        random_trader_args = config[scenario_name].get("random_trader_args", {})
        sensitive_trader_args = config[scenario_name].get("sensitive_trader_args", {})
        sensitive_trader_args = config[scenario_name].get("sensitive_trader_args", {})
        simulation_args = config[scenario_name].get("sensitive_trader_args", {})

        missing = lambda key: f"missing-{key}-for-{scenario_name}"


        result[scenario_name] = lambda: DevOpsScenario(
        binance_code="ETHDAI",
        market_manager_args=MarketManagerArgs(
            market_name=str(market_manager_args.get("market_name", missing("market-name"))),
            market_code=str(market_manager_args.get("market_name", missing("market-code"))),
            asset_name=str(market_manager_args.get("asset_name", missing("asset-name"))),
            adp=int(market_manager_args.get("adp", missing("adp"))),
            mdp=int(market_manager_args.get("mdp", missing("mdp"))),
            pdp=int(market_manager_args.get("pdp", missing("pdp"))),
        ),
        market_maker_args=MarketMakerArgs(
            market_kappa=int(market_maker_args.get("market_kappa", missing("market_kappa"))),
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
            granularity=dispatch_granularity(simulation_args.get("granularity", "MINUTE")),
            coinbase_code=str(simulation_args.get("coinbase_code", missing("coinbase_code"))),
            start_date=str(simulation_args.get("start_date", missing("start_date"))),
            randomise_history=dispatch_bool(simulation_args.get("randomise_history", False)),
        ),
    ),

def dispatch_bool(val: str) -> bool:
    return val.lower() in ["true", "t", "on"]

def dispatch_granularity(val: str) -> Granularity:
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
