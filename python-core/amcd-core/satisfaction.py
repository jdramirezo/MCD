## This file will implement the satisfaction function, which will be used to 
# calculate the satisfaction of each alternative for each criterion. 
# The satisfaction function will be based on the direction of the criterion (max or min) 
# and the threshold and bare minimum values.

from pathlib import Path
from loadData import load_criteria, load_alternatives
import numpy as np

def calculate_satisfaction(alternative, criterion):
    value = alternative.values[criterion.name]
    if criterion.direction == "max":
        if value  >= criterion.bare_minimum:
            return int(1)
        elif value < criterion.bare_minimum:
            return int(0)
    elif criterion.direction == "min":
        if value <= criterion.bare_minimum:
            return int(1)
        elif value > criterion.bare_minimum:
            return int(0)
    else:
        raise ValueError(f"Unknown direction: {criterion.direction}")

def satisfaction_matrix(alternatives, criteria):
    matrix = np.zeros((len(alternatives), len(criteria)))
    results = {}
    for i, alt in enumerate(alternatives):
        for j, crit in enumerate(criteria):
            matrix[i][j] = calculate_satisfaction(alt, crit)
        results[alt.name] = matrix[i]
    return matrix, results


def print_results(results):
    # Order the results by satisfaction score (sum of the satisfaction values)
    sorted_results = sorted(results.items(), key=lambda x: sum(x[1]), reverse=True)
    # eliminated countries
    eliminated_alternatives = [alt for alt, satisfaction in sorted_results if sum(satisfaction) == 0]
    for i in range(len(eliminated_alternatives)):
        sorted_results.pop(-1)
    print("Eliminated alternatives:")
    for alt in eliminated_alternatives:
        print(alt)
    print("\nSatisfaction scores:")
    for alt_name, satisfaction in sorted_results:
        print(f"{alt_name}: {satisfaction}")
    return sorted_results

if __name__ == "__main__":
    
    criteria = load_criteria(Path(f"test/criteria.json"))
    alternatives = load_alternatives(Path(f"test/alternatives.csv"))
    # Filter the non-numeric, non-bare_minimum values from the criteria
    criteria = [crit for crit in criteria if crit.type == "numeric" and crit.family == 'economic' and crit.bare_minimum is not None and crit.weight > 0 ]
    alternatives = [alt for alt in alternatives if all(isinstance(alt.values[crit.name], (int, float)) for crit in criteria)]
    
    matrix, results = satisfaction_matrix(alternatives, criteria)
    print("citeria considered for the satisfaction function:")
    for crit in criteria:
        print(crit.name, crit.direction, crit.bare_minimum)
    print("\nSatisfaction results:")
    print_results(results)