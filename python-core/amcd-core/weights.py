import pandas as pd

from loadData import load_criteria, load_alternatives, load_scenarios
from domain import Critere, Alternative, Direction, Scenario
from pathlib import Path

def calculate_mean(alternatives: list[Alternative], criteria: list[Critere], scenario: Scenario) -> dict[str, float]:
    """Calculate the mean value for each alternative, considering the weights of the criteria."""
    means = {}
    final_weights = dict()
    for family in scenario.weights:
        family_weight = scenario.weights[family]
        family_weights = [crit.weight * family_weight / sum(crit.weight for crit in criteria if crit.family == family) for crit in criteria]
        for crit in criteria:
            if crit.family == family:
                final_weights[crit.name] = family_weights[criteria.index(crit)]
    for alt in alternatives:
        values = [alt.values.get(crit.name, 0) for crit in criteria]
        weighted_sum = sum(value * final_weights.get(crit.name, 0) for value, crit in zip(values, criteria))
        means[alt.name] = weighted_sum 
    return means

def calculate_multiple_means(alternatives_list: list[tuple[list[Alternative], str]], criteria: list[Critere], scenarios: list[Scenario]) -> dict[str, dict[str, float]]:
    """Calculate the mean value for each list of alternatives."""
    means  = {}
    for scenario in scenarios:
        means[scenario.name] = {}    
        for alternatives, name in alternatives_list:
            means[scenario.name][name] = calculate_mean(alternatives, criteria, scenario)
    return means
    

if __name__ == "__main__":
    # weighting methods used a scaled ans normalized version of the data, so we need to load the normalised data instead of the original data
    
    criteria = load_criteria(Path(f"test/criteria.json"))
    
    scenarios = load_scenarios(Path(f"test/scenarios.json"))
    
    alternatives_max = load_alternatives(Path(f"test/normalised_data/normalised_max.csv"))
    alternatives_max_min = load_alternatives(Path(f"test/normalised_data/normalised_max_min.csv"))
    alternatives_sum = load_alternatives(Path(f"test/normalised_data/normalised_sum.csv"))
    alternatives_vector = load_alternatives(Path(f"test/normalised_data/normalised_vector.csv"))
    result = calculate_multiple_means([(alternatives_max, "normalised_max"), (alternatives_max_min, "normalised_max_min"), (alternatives_sum, "normalised_sum"), (alternatives_vector, "normalised_vector")], criteria, scenarios)
    for scenario_name, means in result.items():
        print(f"Scenario: {scenario_name} : description: {next(scen.description for scen in scenarios if scen.name == scenario_name)}")
        print(pd.DataFrame(means))