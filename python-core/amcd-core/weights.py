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
    # weighting methods used a scaled ans normalized version of the data, so we need to load the normalised data instead of the original data
    
    criteria = load_criteria(Path(f"test/criteria.json"))
    alternatives = load_alternatives(Path(f"test/normalised_data/set_to_max_scaled.json"))
    
    # we start with set to max scaled data
    
    alternatives_max = load_alternatives(Path(f"test/normalised_data/normalised_max.json"))
    mean_max = calculate_mean(alternatives_max, criteria)
    print("Mean values for normalised max data:")
    for alt_name, mean in mean_max.items():
        print(f"{alt_name}: {mean}")
        
    