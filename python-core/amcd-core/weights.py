"""Weighted aggregation helpers for normalised MCDA alternatives."""

import argparse
from pathlib import Path

import pandas as pd

from loadData import load_criteria, load_alternatives, load_scenarios
from domain import Alternative, Critere, Scenario


def calculate_mean(
    alternatives: list[Alternative],
    criteria: list[Critere],
    scenario: Scenario,
) -> dict[str, float]:
    """Calculate weighted scores for alternatives under one scenario.

    Scenario-level family weights are first distributed across the criteria in
    each family. Each alternative score is then the sum of its normalised
    criterion values multiplied by those final criterion weights.

    Args:
        alternatives: Normalised alternatives to aggregate.
        criteria: Criteria used for weighting.
        scenario: Scenario defining family weights.

    Returns:
        A mapping from alternative name to weighted score.
    """

    means = {}
    final_weights = dict()

    # Translate scenario family weights into per-criterion weights.
    for family in scenario.weights:
        family_weight = scenario.weights[family]
        family_weights = [
            crit.weight
            * family_weight
            / sum(crit.weight for crit in criteria if crit.family == family)
            for crit in criteria
        ]
        for crit in criteria:
            if crit.family == family:
                final_weights[crit.name] = family_weights[criteria.index(crit)]

    for alt in alternatives:
        values = [alt.values.get(crit.name, 0) for crit in criteria]
        weighted_sum = sum(
            value * final_weights.get(crit.name, 0)
            for value, crit in zip(values, criteria)
        )
        means[alt.name] = weighted_sum
    return means


def calculate_multiple_means(
    alternatives_list: list[tuple[list[Alternative], str]],
    criteria: list[Critere],
    scenarios: list[Scenario],
) -> dict[str, dict[str, float]]:
    """Calculate weighted scores for several normalisation methods.

    Args:
        alternatives_list: Pairs of ``(alternatives, method_name)``.
        criteria: Criteria used for weighting.
        scenarios: Scenarios under which scores should be computed.

    Returns:
        Nested mapping of ``scenario_name -> method_name -> scores``.
    """

    means = {}
    for scenario in scenarios:
        means[scenario.name] = {}
        for alternatives, name in alternatives_list:
            means[scenario.name][name] = calculate_mean(alternatives, criteria, scenario)
    return means


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for weighted aggregation.

    Returns:
        Parsed CLI arguments.
    """

    parser = argparse.ArgumentParser(
        description="Run weighted aggregation for normalised MCDA alternatives."
    )
    parser.add_argument(
        "--normalised_data",
        type=Path,
        default=None,
        help="Folder containing normalised alternatives.",
    )
    parser.add_argument("--criteria", type=Path, default=Path("test/criteria.json"))
    parser.add_argument(
        "--alternatives",
        type=Path,
        default=Path("test/alternatives.csv"),
    )
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--scenarios", type=Path, default=Path("test/scenarios.json"))
    return parser.parse_args()


if __name__ == "__main__":
    # Weighted aggregation uses the normalised datasets produced upstream.

    args = parse_args()

    criteria = load_criteria(args.criteria)
    _alternatives = load_alternatives(args.alternatives)
    scenarios = load_scenarios(args.scenarios)

    alternatives_max = load_alternatives(
        Path(args.normalised_data / "normalised_max.csv")
    )
    alternatives_max_min = load_alternatives(
        Path(args.normalised_data / "normalised_max_min.csv")
    )
    alternatives_sum = load_alternatives(Path(args.normalised_data / "normalised_sum.csv"))
    alternatives_vector = load_alternatives(
        Path(args.normalised_data / "normalised_vector.csv")
    )

    # Compare all normalisation methods under every scenario.
    result = calculate_multiple_means(
        [
            (alternatives_max, "normalised_max"),
            (alternatives_max_min, "normalised_max_min"),
            (alternatives_sum, "normalised_sum"),
            (alternatives_vector, "normalised_vector"),
        ],
        criteria,
        scenarios,
    )
    for scenario_name, means in result.items():
        description = next(
            scen.description for scen in scenarios if scen.name == scenario_name
        )
        print(f"Scenario: {scenario_name} : description: {description}")
        print(pd.DataFrame(means))
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            for scenario_name, means in result.items():
                description = next(
                    scen.description for scen in scenarios if scen.name == scenario_name
                )
                f.write(f"Scenario: {scenario_name} : description: {description}\n")
                df = pd.DataFrame(means)
                # Preserve the alternative name as an explicit CSV column.
                df.insert(0, "Alternative", df.index)
                df.to_csv(f, index=False)
                f.write("\n")
        print(f"Mean values saved to {args.output}")
