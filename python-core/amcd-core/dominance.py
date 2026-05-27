"""Pareto-style dominance filtering for MCDA alternatives."""

import argparse
from pathlib import Path

import pandas as pd

from loadData import load_criteria, load_alternatives
from domain import Critere, Alternative, Direction


def is_dominated(
    alt1: Alternative,
    alt2: Alternative,
    criteria: list[Critere],
) -> bool:
    """Check whether one alternative is dominated by another.

    ``alt1`` is dominated when ``alt2`` is at least as good on every available
    criterion after accounting for each criterion's indifference threshold.
    Values inside the threshold are treated as equivalent.

    Args:
        alt1: Alternative being tested for dominance.
        alt2: Alternative used as the possible dominator.
        criteria: Criteria used for pairwise comparison.

    Returns:
        ``True`` when ``alt2`` dominates ``alt1``; otherwise ``False``.
    """

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

    # alt1 is dominated if alt2 is never worse across the selected criteria.
    better_in_all = any(b == '<' or b == '=' for b in better_list) and not any(
        b == '>' for b in better_list
    )

    # Print the comparison detail only when a dominance relation is found.
    if better_in_all:
        print(f"{alt1.name} is dominated by {alt2.name} based on criteria:")
        for crit, b in zip(criteria, better_list):
            print(f"  - {crit.name}: {b}")
    return better_in_all


def find_non_dominated(
    alternatives: list[Alternative],
    criteria: list[Critere],
) -> list[Alternative]:
    """Return alternatives that are not dominated by any other alternative.

    Args:
        alternatives: Alternatives to compare pairwise.
        criteria: Criteria used for the dominance test.

    Returns:
        Alternatives for which no dominating alternative was found.
    """

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


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for dominance analysis.

    Returns:
        Parsed CLI arguments.
    """

    parser = argparse.ArgumentParser(
        description="Run dominance analysis for MCDA alternatives."
    )
    parser.add_argument(
        "--satisfaction_output",
        type=Path,
        default=None,
        help="CSV file containing alternatives retained by satisfaction analysis.",
    )
    parser.add_argument("--criteria", type=Path, default=Path("test/criteria.json"))
    parser.add_argument(
        "--alternatives",
        type=Path,
        default=Path("test/alternatives.csv"),
    )
    parser.add_argument("--family", nargs="+", default=["economic"])
    parser.add_argument("--output", type=Path, default=None)

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    criteria = load_criteria(args.criteria)
    alternatives = load_alternatives(args.alternatives)

    # Dominance only uses active numeric criteria in the selected families.
    criteria = [
        crit for crit in criteria
        if crit.type == "numeric"
        and crit.family in args.family
        and crit.bare_minimum is not None
        and crit.weight > 0
    ]

    satisfaction_alts = args.satisfaction_output
    # Restrict the analysis to alternatives retained by satisfaction filtering.
    if satisfaction_alts is not None:
        retained_alts = pd.read_csv(satisfaction_alts)['alternative'].tolist()
    else:
        retained_alts = [alt.name for alt in alternatives]

    # Pairwise comparisons assume every selected criterion has a numeric value.
    alternatives = [
        alt for alt in alternatives
        if all(
            isinstance(alt.values[crit.name], (int, float))
            for crit in criteria
        )
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
