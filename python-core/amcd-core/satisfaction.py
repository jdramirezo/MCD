"""Satisfaction filtering for MCDA alternatives.

This module checks whether each alternative reaches the bare minimum required
by each numeric criterion. Alternatives with no satisfied criteria are reported
as eliminated before later dominance and weighting steps.
"""

import argparse
import csv
from pathlib import Path

import numpy as np

from domain import Alternative, Critere
from loadData import load_criteria, load_alternatives


def calculate_satisfaction(alternative: Alternative, criterion: Critere) -> int:
    """Return whether an alternative satisfies one criterion.

    For ``max`` criteria, values must be greater than or equal to the bare
    minimum. For ``min`` criteria, values must be less than or equal to it.

    Args:
        alternative: Alternative containing a value for the criterion.
        criterion: Criterion defining the direction and bare minimum.

    Returns:
        ``1`` when the criterion is satisfied, otherwise ``0``.

    Raises:
        ValueError: If the criterion direction is not ``max`` or ``min``.
    """

    value = alternative.values[criterion.name]
    if criterion.direction == "max":
        if value >= criterion.bare_minimum:
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


def satisfaction_matrix(
    alternatives: list[Alternative],
    criteria: list[Critere],
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """Build the binary satisfaction matrix for alternatives and criteria.

    Args:
        alternatives: Alternatives to evaluate.
        criteria: Criteria used for the satisfaction check.

    Returns:
        A tuple containing the raw NumPy matrix and a dictionary keyed by
        alternative name with that alternative's satisfaction row.
    """

    matrix = np.zeros((len(alternatives), len(criteria)))
    results = {}

    for i, alt in enumerate(alternatives):
        for j, crit in enumerate(criteria):
            matrix[i][j] = calculate_satisfaction(alt, crit)
        results[alt.name] = matrix[i]
    return matrix, results


def print_results(
    results: dict[str, np.ndarray],
) -> tuple[list[tuple[str, np.ndarray]], list[str]]:
    """Print and separate retained and eliminated alternatives.

    Alternatives are sorted by the number of satisfied criteria. Any
    alternative with a total score of zero is considered eliminated.

    Args:
        results: Mapping from alternative name to satisfaction row.

    Returns:
        A tuple containing retained alternatives with their satisfaction rows
        and a list of eliminated alternative names.
    """

    # Order the results by satisfaction score (sum of the satisfaction values)
    sorted_results = sorted(results.items(), key=lambda x: sum(x[1]), reverse=True)

    # Alternatives with no satisfied criteria are removed from later steps.
    eliminated_alternatives = [
        alt for alt, satisfaction in sorted_results if sum(satisfaction) == 0
    ]
    for _ in range(len(eliminated_alternatives)):
        sorted_results.pop(-1)

    print("Eliminated alternatives:")
    for alt in eliminated_alternatives:
        print(alt)
    return sorted_results, eliminated_alternatives


def write_results_to_csv(
    retained_alternatives: list[tuple[str, np.ndarray]],
    eliminated_alternatives: list[str],
    output_file: Path,
) -> None:
    """Write satisfaction results to a CSV file.

    Retained and eliminated names are written in separate columns. The lists are
    padded before writing so both columns keep all values even when their
    lengths differ.

    Args:
        retained_alternatives: Alternatives that passed satisfaction filtering.
        eliminated_alternatives: Names of alternatives eliminated by the filter.
        output_file: Destination CSV path.
    """

    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Extract names from retained tuples of (name, satisfaction_array).
    retained_names = [alt[0] for alt in retained_alternatives]

    # Pad lists to equal length to avoid data loss
    max_len = max(len(retained_names), len(eliminated_alternatives))
    retained_names_padded = retained_names + [""] * (max_len - len(retained_names))
    eliminated_padded = eliminated_alternatives + [""] * (
        max_len - len(eliminated_alternatives)
    )

    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["alternative", "eliminated"])
        for retained, eliminated in zip(retained_names_padded, eliminated_padded):
            writer.writerow([retained, eliminated])


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for satisfaction analysis.

    Returns:
        Parsed CLI arguments.
    """

    parser = argparse.ArgumentParser(
        description="Run satisfaction analysis for MCDA alternatives."
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

    # Satisfaction applies only to active numeric criteria in selected families.
    criteria = [
        crit for crit in criteria
        if crit.type == "numeric"
        and crit.family in args.family
        and crit.bare_minimum is not None
        and crit.weight > 0
    ]

    # Later calculations assume numeric values for every selected criterion.
    alternatives = [
        alt for alt in alternatives
        if all(isinstance(alt.values[crit.name], (int, float)) for crit in criteria)
    ]

    matrix, results = satisfaction_matrix(alternatives, criteria)
    sorted_results, eliminated_alternatives = print_results(results)
    if args.output:
        write_results_to_csv(sorted_results, eliminated_alternatives, args.output)
        print(f"\nSaved satisfaction results to {args.output}")
