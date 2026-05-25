## This file will implement the satisfaction function, which will be used to 
# calculate the satisfaction of each alternative for each criterion. 
# The satisfaction function will be based on the direction of the criterion (max or min) 
# and the threshold and bare minimum values.

from pathlib import Path
from loadData import load_criteria, load_alternatives
import numpy as np
import argparse
import csv
from pathlib import Path

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
    return sorted_results, eliminated_alternatives

def write_results_to_csv(results, output_file: Path):
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["alternative", "satisfaction_score"])

        for alt_name, satisfaction in results:
            writer.writerow([
                alt_name,
                int(sum(satisfaction)),
            ])

def parse_args():
    parser = argparse.ArgumentParser(
        description="Run satisfaction analysis for MCDA alternatives."
    )

    parser.add_argument("--criteria", type=Path, default=Path("test/criteria.json"))
    parser.add_argument("--alternatives", type=Path, default=Path("test/alternatives.csv"))
    parser.add_argument("--family", nargs="+", default=["economic"])
    parser.add_argument("--output", type=Path, default=None)

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    criteria = load_criteria(args.criteria)
    alternatives = load_alternatives(args.alternatives)
    
    criteria = [
        crit for crit in criteria
        if crit.type == "numeric"
        and crit.family in args.family
        and crit.bare_minimum is not None
        and crit.weight > 0
    ]
    
    alternatives = [
        alt for alt in alternatives
        if all(isinstance(alt.values[crit.name], (int, float)) for crit in criteria)
    ]
    
    matrix, results = satisfaction_matrix(alternatives, criteria)
    sorted_results, eliminated_alternatives = print_results(results)
    if args.output:
        write_results_to_csv(sorted_results, args.output)
        print(f"\nSaved satisfaction results to {args.output}")