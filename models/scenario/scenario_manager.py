class ScenarioManager:
    def __init__(self):
        self.scenarios = []

    def add_scenario(self, scenario):
        self.scenarios.append(scenario)

    def reset_timesteps(self, scenario):
        for aux in scenario.auxiliaries:
            aux.current_time_step = 0

    def run_all(self, simulation_time, dt):
        for scenario in self.scenarios:
            self.reset_timesteps(scenario)
            scenario.run(simulation_time, dt)

    def get_results(self, scenario_name):
        for scenario in self.scenarios:
            if scenario.name == scenario_name:
                return scenario.results
        return None
