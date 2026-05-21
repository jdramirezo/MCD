from loadData import load_criteria, load_alternatives
from domain import Critere, Alternative, Direction
from normalize import NormalisedData
from pathlib import Path

def calculate_mean(alternatives: list[Alternative], criteria: list[Critere]) -> dict[str, float]:
    """Calculate the mean value for each alternative, considering the weights of the criteria."""
    means = {}
    for alt in alternatives:
        values = [alt.values.get(crit.name, 0) for crit in criteria]
        weights = [crit.weight for crit in criteria]
        weighted_sum = sum(value * weight for value, weight in zip(values, weights))
        means[alt.name] = weighted_sum 
    return means

if __name__ == "__main__":
    criteria = [crit for crit in load_criteria(Path(f"test/criteria.json")) if crit.type == "numeric" and crit.weight > 0 ]
    alternatives = [alt for alt in load_alternatives(Path(f"test/alternatives.csv")) if all(isinstance(alt.values[crit.name], (int, float)) for crit in criteria)]
    normalised_data = NormalisedData(alternatives, criteria).scale_to_number.normalise_max_min()
    means = calculate_mean(alternatives, criteria)
    print("Mean values for each alternative:")
    for alt_name, mean in means.items():
        print(f"{alt_name}: {mean}")