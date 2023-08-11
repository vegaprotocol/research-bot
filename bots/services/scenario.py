from bots.services.service import Service
from bots.services.multiprocessing import threaded

from vega_sim.scenario.constants import Network
from vega_sim.devops.scenario import DevOpsScenario
from vega_sim.network_service import VegaServiceNetwork

class ScenarioService(Service):
    network_to_vega_sim_id = {
        "devnet1": "DEVNET1",
        "stagnet1": "STAGNET1",
        "fairground": "FAIRGROUND",
        "mainnet-mirror": "MAINNET_MIRROR"
    }

    def __init__(self, vega: VegaServiceNetwork, network: str, scenario: DevOpsScenario) -> None:
        self.vega = vega
        self.network = network
        self.scenario = scenario

    @threaded
    def start(self):
        self.scenario.run_iteration(
            vega=self.vega,
            network=Network[self.network],
            pause_at_completion=False,
            raise_datanode_errors=False,
            raise_step_errors=False,
            run_with_snitch=False,
        )