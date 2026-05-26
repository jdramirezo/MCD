import argparse

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

def parse_args():
    parser = argparse.ArgumentParser(
        description="Run dominance analysis for MCDA alternatives."
    )
    parser.add_argument("--normalised_data", type=Path, default=None, help="Path to save the satisfaction analysis results as a CSV file.")
    parser.add_argument("--criteria", type=Path, default=Path("test/criteria.json"))
    parser.add_argument("--alternatives", type=Path, default=Path("test/alternatives.csv"))
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--scenarios", type=Path, default=Path("test/scenarios.json"))
    return parser.parse_args()

if __name__ == "__main__":
    # weighting methods used a scaled ans normalized version of the data, so we need to load the normalised data instead of the original data
    
    args = parse_args()
    
    criteria = load_criteria(args.criteria)
    alternatives = load_alternatives(args.alternatives)
    scenarios = load_scenarios(args.scenarios)
    
    alternatives_max = load_alternatives(Path(args.normalised_data / "normalised_max.csv"))
    alternatives_max_min = load_alternatives(Path(args.normalised_data / "normalised_max_min.csv"))
    alternatives_sum = load_alternatives(Path(args.normalised_data / "normalised_sum.csv"))
    alternatives_vector = load_alternatives(Path(args.normalised_data / "normalised_vector.csv"))

    result = calculate_multiple_means([(alternatives_max, "normalised_max"), (alternatives_max_min, "normalised_max_min"), (alternatives_sum, "normalised_sum"), (alternatives_vector, "normalised_vector")], criteria, scenarios)
    for scenario_name, means in result.items():
        print(f"Scenario: {scenario_name} : description: {next(scen.description for scen in scenarios if scen.name == scenario_name)}")
        print(pd.DataFrame(means))
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w') as f:
            for scenario_name, means in result.items():
                f.write(f"Scenario: {scenario_name} : description: {next(scen.description for scen in scenarios if scen.name == scenario_name)}\n")
                #create a dataframe from the mean but place the name of the alternative as the index and the mean value as a column
                df = pd.DataFrame(means)
                #add a column with the name of the alternative
                df.insert(0, 'Alternative', df.index)
                df.to_csv(f, index=False)
                f.write("\n")
        print(f"Mean values saved to {args.output}")