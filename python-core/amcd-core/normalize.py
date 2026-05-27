"""Normalisation helpers for MCDA alternatives."""

import argparse
import csv
from copy import deepcopy
from pathlib import Path

import pandas as pd

from domain import Critere, Alternative, Direction, Scenario
from loadData import load_criteria, load_alternatives, load_scenarios


def format_markdown_table(alternatives: list[Alternative], criteria: list[Critere]) -> str:
    """Format alternatives and criterion values as a Markdown table.

    Args:
        alternatives: Alternatives to display.
        criteria: Criteria to include as columns.

    Returns:
        A Markdown table string.
    """

    headers = ["Alternative", *[criterion.name for criterion in criteria]]
    separator = ["---"] * len(headers)
    rows = []

    for alternative in alternatives:
        row = [alternative.name]
        for criterion in criteria:
            value = alternative.values.get(criterion.name, "")
            if isinstance(value, (int, float)):
                row.append(f"{value:.4f}")
            else:
                row.append(str(value))
        rows.append(row)

    table_lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(separator) + " |",
    ]
    table_lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(table_lines)


def write_list_of_alternatives_to_csv(
    alternatives: list[Alternative],
    criteria: list[Critere],
    filename: str | Path,
) -> None:
    """Write alternatives and selected criterion values to a CSV file.

    Args:
        alternatives: Alternatives to write.
        criteria: Criteria to include as columns.
        filename: Destination CSV path.
    """

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["name", *[criterion.name for criterion in criteria]])
        for alternative in alternatives:
            row = [alternative.name] + [
                alternative.values.get(criterion.name, "")
                for criterion in criteria
            ]
            writer.writerow(row)


def normalise_max(alternatives: list[Alternative], criteria: list[Critere]) -> list[Alternative]:
    """Normalise values by dividing by the criterion maximum.

    Formula for ``max`` criteria: ``value / max(values) * 100``.
    For ``min`` criteria, the score is inverted so lower raw values receive
    higher normalised scores.

    Args:
        alternatives: Alternatives to normalise.
        criteria: Numeric criteria to transform.

    Returns:
        A deep-copied list of alternatives with normalised values.
    """

    result = deepcopy(alternatives)
    for crit in criteria:
        max_value = max(alt.values[crit.name] for alt in result)
        for alt in result:
            if crit.direction == Direction.MAX:
                alt.values[crit.name] = (
                    alt.values[crit.name] / max_value * 100
                    if max_value != 0
                    else 0
                )
            else:
                alt.values[crit.name] = (
                    (1 - alt.values[crit.name] / max_value) * 100
                    if max_value != 0
                    else 0
                )
    return result


def normalise_max_min(
    alternatives: list[Alternative],
    criteria: list[Critere],
) -> list[Alternative]:
    """Normalise values using min-max scaling.

    Formula for ``max`` criteria:
    ``(value - min(values)) / (max(values) - min(values)) * 100``.
    For ``min`` criteria, the scaled score is inverted.

    Args:
        alternatives: Alternatives to normalise.
        criteria: Numeric criteria to transform.

    Returns:
        A deep-copied list of alternatives with normalised values.
    """

    result = deepcopy(alternatives)
    for crit in criteria:
        max_value = max(alt.values[crit.name] for alt in result)
        min_value = min(alt.values[crit.name] for alt in result)
        for alt in result:
            if crit.direction == Direction.MAX:
                alt.values[crit.name] = (
                    (alt.values[crit.name] - min_value)
                    / (max_value - min_value)
                    * 100
                    if max_value != min_value
                    else 0
                )
            else:
                alt.values[crit.name] = (
                    (
                        1
                        - (alt.values[crit.name] - min_value)
                        / (max_value - min_value)
                    )
                    * 100
                    if max_value != min_value
                    else 0
                )
    return result


def normalise_sum(alternatives: list[Alternative], criteria: list[Critere]) -> list[Alternative]:
    """Normalise values by dividing by the criterion sum.

    Formula for ``max`` criteria: ``value / sum(values) * 100``.
    For ``min`` criteria, the score is inverted.

    Args:
        alternatives: Alternatives to normalise.
        criteria: Numeric criteria to transform.

    Returns:
        A deep-copied list of alternatives with normalised values.
    """

    result = deepcopy(alternatives)
    for crit in criteria:
        sum_value = sum(alt.values[crit.name] for alt in result)
        for alt in result:
            if crit.direction == Direction.MAX:
                alt.values[crit.name] = (
                    alt.values[crit.name] / sum_value * 100
                    if sum_value != 0
                    else 0
                )
            else:
                alt.values[crit.name] = (
                    (1 - alt.values[crit.name] / sum_value) * 100
                    if sum_value != 0
                    else 0
                )
    return result


def normalise_vector(
    alternatives: list[Alternative],
    criteria: list[Critere],
) -> list[Alternative]:
    """Normalise values by the Euclidean norm of each criterion.

    Formula for ``max`` criteria: ``value / sqrt(sum(values^2)) * 100``.
    For ``min`` criteria, the score is inverted.

    Args:
        alternatives: Alternatives to normalise.
        criteria: Numeric criteria to transform.

    Returns:
        A deep-copied list of alternatives with normalised values.
    """

    result = deepcopy(alternatives)
    for crit in criteria:
        sum_squares = sum(alt.values[crit.name] ** 2 for alt in result)
        norm = sum_squares ** 0.5
        for alt in result:
            if crit.direction == Direction.MAX:
                alt.values[crit.name] = (
                    alt.values[crit.name] / norm * 100
                    if norm != 0
                    else 0
                )
            else:
                alt.values[crit.name] = (
                    (1 - alt.values[crit.name] / norm) * 100
                    if norm != 0
                    else 0
                )
    return result


def normalise_for_electra(
    alternatives: list[Alternative],
    criteria: list[Critere],
) -> list[Alternative]:
    """Prepare criterion values for the ELECTRE concordance calculation.

    ``min`` criteria are converted so larger values are better, then values are
    scaled by the criterion threshold when one exists. Criteria without a
    threshold are multiplied by ``10`` to keep them on a comparable scale.

    Args:
        alternatives: Alternatives to normalise.
        criteria: Numeric criteria used by ELECTRE.

    Returns:
        A deep-copied list of alternatives with ELECTRE-ready values.
    """

    result = deepcopy(alternatives)
    for crit in criteria:
        threshold = getattr(crit, "threshold", None)
        max_value = max(alt.values[crit.name] for alt in result)
        # ELECTRE comparison expects all criteria to point in the same direction.
        if crit.direction == Direction.MIN:
            for alt in result:
                alt.values[crit.name] = max_value - alt.values.get(crit.name, 0)

        for alt in result:
            if threshold is None or threshold == 0:
                alt.values[crit.name] = alt.values.get(crit.name, 0) * 10
            else:
                alt.values[crit.name] = alt.values.get(crit.name, 0) / threshold
    return result


def save_normalised_data(
    alternatives: list[Alternative],
    criteria: list[Critere],
    output_folder: Path,
    scenarios: list[Scenario],
) -> None:
    """Save all normalised datasets used by later pipeline steps.

    The function writes one CSV for each generic normalisation method and one
    ELECTRE-specific CSV per scenario.

    Args:
        alternatives: Alternatives to normalise and save.
        criteria: Criteria included in the output files.
        output_folder: Folder where CSV files will be created.
        scenarios: Scenarios used to name the ELECTRE-specific files.
    """

    output_folder.mkdir(exist_ok=True)

    # Each file preserves the same columns so downstream scripts can swap methods.
    file = output_folder / "normalised_max.csv"
    write_list_of_alternatives_to_csv(
        normalise_max(deepcopy(alternatives), criteria),
        criteria,
        file,
    )

    file = output_folder / "normalised_max_min.csv"
    write_list_of_alternatives_to_csv(
        normalise_max_min(deepcopy(alternatives), criteria),
        criteria,
        file,
    )

    file = output_folder / "normalised_sum.csv"
    write_list_of_alternatives_to_csv(
        normalise_sum(deepcopy(alternatives), criteria),
        criteria,
        file,
    )

    file = output_folder / "normalised_vector.csv"
    write_list_of_alternatives_to_csv(
        normalise_vector(deepcopy(alternatives), criteria),
        criteria,
        file,
    )

    for scenario in scenarios:
        file = output_folder / f"normalised_electre_{scenario.name}.csv"
        write_list_of_alternatives_to_csv(
            normalise_for_electra(deepcopy(alternatives), criteria),
            criteria,
            file,
        )

    print(f" /n -----Normalised data saved to {output_folder}---- /n ")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for normalisation.

    Returns:
        Parsed CLI arguments.
    """

    parser = argparse.ArgumentParser(
        description="Normalise MCDA alternatives for downstream analysis."
    )
    parser.add_argument(
        "--dominance_output",
        type=Path,
        default=None,
        help="CSV file containing alternatives retained by dominance analysis.",
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
    args = parse_args()
    criteria = load_criteria(args.criteria)
    alternatives = load_alternatives(args.alternatives)

    # Normalisation only uses active numeric criteria.
    criteria = [
        crit for crit in criteria
        if crit.type == "numeric"
        and crit.weight > 0
    ]

    domination_alts = args.dominance_output
    # Restrict normalisation to alternatives retained by dominance filtering.
    if domination_alts is not None:
        retained_alts = pd.read_csv(domination_alts)['name'].tolist()
    else:
        retained_alts = [alt.name for alt in alternatives]

    # The normalisation formulas require numeric values for every criterion.
    alternatives = [
        alt for alt in alternatives
        if all(
            isinstance(alt.values[crit.name], (int, float))
            for crit in criteria
        )
        and alt.name in retained_alts
    ]
    scenarios = load_scenarios(args.scenarios)
    save_normalised_data(alternatives, criteria, args.output, scenarios)
