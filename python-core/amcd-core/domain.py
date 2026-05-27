"""Shared domain models for the MCDA pipeline."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class Direction(str, Enum):
    """Optimization direction used by a criterion."""

    MAX = "max"
    MIN = "min"


@dataclass
class Critere:
    """Decision criterion used to score and filter alternatives.

    Attributes:
        name: Column name used by alternatives for this criterion.
        direction: Whether higher or lower values are preferred.
        type: Data type category, for example ``numeric``.
        weight: Weight of this criterion inside its family.
        threshold: Indifference threshold used by dominance/ELECTRE logic.
        bare_minimum: Minimum acceptable value for satisfaction filtering.
        categories: Optional allowed categories for non-numeric criteria.
        family: Criterion family used by scenario-level weights.
    """

    name: str
    direction: Direction
    type: str
    weight: float
    threshold: float = 0.0
    bare_minimum: float = 0.0
    categories: list[str] | None = None
    family: str | None = None


@dataclass
class Alternative:
    """Candidate evaluated by the decision-making process.

    Attributes:
        name: Human-readable alternative name.
        values: Mapping from criterion name to the alternative value.
    """

    name: str
    values: dict[str, Any]


@dataclass
class Scenario:
    """Weighting scenario applied to criterion families.

    Attributes:
        name: Scenario identifier used in output filenames.
        description: Human-readable explanation of the scenario.
        weights: Mapping from criterion family name to family weight.
    """

    name: str
    description: str
    weights: dict[str, float]
