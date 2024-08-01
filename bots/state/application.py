import bots.config.types

class ApplicationState:
    def __init__(self, config: bots.config.types.BotsConfig):
        self._config = config

    @property
    def shrinked_scenarios() -> bots.config.types.ScenariosConfigType:
        """
        In case We want to split our scenarios to smaller pieces, we shrink them to have 
        certain amount of traders per scenario. Each scenario runs in the separated threads.
        Each trader executes steps in the loop, so We have to split execution to multiple
        processes. This function prepares scenarios
        """
        result = bots.config.types.ScenariosConfigType()
        for scenario_name, scenario_config in self._config.scenarios.items():
            pass