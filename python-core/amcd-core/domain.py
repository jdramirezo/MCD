from dataclasses import dataclass
from enum import Enum
from typing import Any

class Direction(str, Enum):
    MAX = "max"
    MIN = "min"
    
@dataclass
class Critere:
    name: str
    direction: Direction
    type: str
    weight: float
    threshold: float = 0.0
    bare_minimum: float = 0.0
    categories: list[str] | None = None
    family : str | None = None
    
@dataclass
class Alternative:
    """This class represents an alternative.
    Meaning a suitable candidate for the decision making process.
    """
    name: str
    values: dict[str, Any]
    
@dataclass
class Scenario:
    name: "str"
    description: "str"
    weights: dict[str, float]