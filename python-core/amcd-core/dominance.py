import argparse
import csv

import pandas as pd

from loadData import load_criteria, load_alternatives
from domain import Critere, Alternative, Direction
from pathlib import Path

def is_dominated(alt1: Alternative, alt2: Alternative, criteria: list[Critere]) -> bool:
    """Check if alt1 is dominated by alt2 based on the criteria."""
    better_list = [False for _ in criteria]
    for crit in criteria:
        indifference_threshold = crit.threshold if crit.threshold is not None else 0
        val1 = alt1.values.get(crit.name)
        val2 = alt2.values.get(crit.name)
        if val1 is None or val2 is None:
            continue  # Skip if criterion value is missing
        if abs(val1 - val2) <= indifference_threshold:
            better_list[criteria.index(crit)] = '='
        elif abs(val1 - val2) > indifference_threshold:
            if crit.direction == Direction.MAX:
                # alt1 is dominated by alt2 if val1 < val2
                better_list[criteria.index(crit)] = '<' if val1 < val2 else '>'
            elif crit.direction == Direction.MIN:
                # alt 1 is dominated by alt2 if val2 < val1
                better_list[criteria.index(crit)] = '<' if val2 < val1 else '>'
    # alt1 is dominated by alt2 if alt2 is better in at least one criterion and not worse in any criterion
    better_in_all = any(b == '<' or b == '=' for b in better_list) and not any(b == '>' for b in better_list)
    return better_in_all

def find_non_dominated(alternatives: list[Alternative], criteria: list[Critere]) -> list[Alternative]:
    """Return a list of non-dominated alternatives"""
    non_dominated = []
    for alt in alternatives:
        dominated = False
        for other in alternatives:
            if alt != other and is_dominated(alt, other, criteria):
                dominated = True
                break
        if not dominated:
            non_dominated.append(alt)
    return non_dominated

def parse_args():
    parser = argparse.ArgumentParser(
        description="Run dominance analysis for MCDA alternatives."
    )
    parser.add_argument("--satisfaction_output", type=Path, default=None, help="Path to save the satisfaction analysis results as a CSV file.")
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
    
    satisfaction_alts = args.satisfaction_output
    # read the retained alt from the satisfaction analysis if the file exists
    if satisfaction_alts is not None:
        retained_alts = pd.read_csv(satisfaction_alts)['alternative'].tolist()
    else:
        retained_alts = [alt.name for alt in alternatives]
    
    alternatives = [
        alt for alt in alternatives
        if all(isinstance(alt.values[crit.name], 
                          (int, float)) for crit in criteria)
        and alt.name in retained_alts
    ]
    
    non_dominated = find_non_dominated(alternatives, criteria)
    df = pd.DataFrame(non_dominated)
    
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(args.output, index=False)
        print(f"Non-dominated alternatives saved to {args.output}")
    else:
        print("No output file specified. Skipping save.")