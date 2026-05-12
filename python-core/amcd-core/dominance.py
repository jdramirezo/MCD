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
    if better_in_all:
        print(f"{alt1.name} is dominated by {alt2.name}")
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

if __name__ == "__main__":
    criteria = load_criteria(Path(f"test/criteria.json"))
    alternatives = load_alternatives(Path(f"test/alternatives.csv"))
    # Filter the non-numeric, non-bare_minimum values from the criteria
    criteria = [crit for crit in criteria if crit.type == "numeric" and crit.family == 'economic' and crit.bare_minimum is not None and crit.weight > 0 ]
    alternatives = [alt for alt in alternatives if all(isinstance(alt.values[crit.name], (int, float)) for crit in criteria)]
    print("Criteria considered for dominance analysis: \n")
    for crit in criteria:
        print(crit.name, crit.direction, crit.bare_minimum)
    non_dominated_alts = find_non_dominated(alternatives, criteria)
    print("\nNon-dominated alternatives:")
    for alt in non_dominated_alts:
        print(alt.name)
    print("\nAlternatives that were dominated by others:")
    for alt in alternatives:
        if alt not in non_dominated_alts:
            print(alt.name)