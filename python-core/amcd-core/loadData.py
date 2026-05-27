"""Load criteria, alternatives, and scenarios from input data files."""

import csv
import json
from pathlib import Path

from domain import Alternative, Critere, Direction, Scenario


def load_criteria(file: Path) -> list[Critere]:
    """Load decision criteria from a JSON file.

    The expected file format contains a top-level ``Criteria`` list. Each item
    is converted into a :class:`Critere` object and missing optional values are
    replaced with the defaults used by the rest of the pipeline.

    Args:
        file: Path to the criteria JSON file.

    Returns:
        A list of criteria in the same order as the JSON input.
    """

    with open(file, "r") as f:
        data = json.load(f)

    criteria_list = []
    for item in data["Criteria"]:
        criterion = Critere(
            name=item["name"],
            direction=Direction(item["direction"]),
            type=item["type"],
            weight=item["weight"],
            threshold=item.get("threshold", 0.0),
            bare_minimum=item.get("bare_minimum", 0.0),
            categories=item.get("categories"),
            family=item.get("family"),
        )
        criteria_list.append(criterion)
    return criteria_list


def load_alternatives(file: Path) -> list[Alternative]:
    """Load alternatives from a CSV file.

    The CSV must include a ``name`` column. Every other column is stored in the
    alternative value mapping and converted to ``float`` when it looks numeric.

    Args:
        file: Path to the alternatives CSV file.

    Returns:
        A list of alternatives with their criterion values.
    """

    alternatives = []
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Keep text values as-is so categorical criteria can be loaded.
            values = {
                k: float(v) if v.replace(".", "", 1).isdigit() else v
                for k, v in row.items()
                if k != "name"
            }
            alt = Alternative(
                name=row["name"],
                values=values,
            )
            alternatives.append(alt)
    return alternatives


def load_scenarios(file: Path) -> list[Scenario]:
    """Load scenario definitions from a JSON file.

    The expected file format contains a top-level ``Scenarios`` list. Scenario
    family weights are kept as provided by the input file.

    Args:
        file: Path to the scenarios JSON file.

    Returns:
        A list of scenarios used by weighting and ELECTRE computations.
    """

    with open(file, "r") as f:
        data = json.load(f)

    scenarios_list = []
    for item in data["Scenarios"]:
        scenario = Scenario(
            name=item["name"],
            description=item["description"],
            weights=item["weights"],
        )
        scenarios_list.append(scenario)
    return scenarios_list


if __name__ == "__main__":
    criteria = load_criteria(Path("test/criteria.json"))
    print("\nLoaded Criteria:")
    for crit in criteria:
        print(crit.name)
    print("\nLoaded Alternatives:")
    alternatives = load_alternatives(Path("test/alternatives.csv"))
    for alt in alternatives:
        print(alt.name)
