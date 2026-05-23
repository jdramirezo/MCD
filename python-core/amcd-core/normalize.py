from domain import Critere, Alternative, Direction
from loadData import load_criteria, load_alternatives
from dataclasses import dataclass, field
from pathlib import Path
import csv
from copy import deepcopy


def format_markdown_table(alternatives: list[Alternative], criteria: list[Critere]) -> str:
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

def write_list_of_alternatives_to_csv(alternatives: list[Alternative], criteria: list[Critere], filename: str):
    """This function will take a list of alternatives and save it to a csv file."""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Alternative", *[criterion.name for criterion in criteria]])
        for alternative in alternatives:
            row = [alternative.name] + [alternative.values.get(criterion.name, "") for criterion in criteria]
            writer.writerow(row)
    
def save_normalised_data(alternatives: list[Alternative], criteria: list[Critere]):
    """This function will take a list of alternatives and criteria and save the normalised version on a separate file."""
    # Create folder if it doesn't exist
    output_folder = Path("test/normalised_data")
    output_folder.mkdir(exist_ok=True)
    
    # Save "normalised max" data to a csv file
    normal_data = NormalisedData(alternatives, criteria)
    file = output_folder / "normalised_max.csv"
    write_list_of_alternatives_to_csv(normal_data.normalise_max().alternatives, criteria, file)
    
    # Save "normalised max-min" data to a csv file
    normal_data = NormalisedData(alternatives, criteria)
    file = output_folder / "normalised_max_min.csv"
    write_list_of_alternatives_to_csv(normal_data.normalise_max_min().alternatives, criteria, file)
    
    # Save "normalised sum" data to a csv file
    normal_data = NormalisedData(alternatives, criteria)
    file = output_folder / "normalised_sum.csv"
    write_list_of_alternatives_to_csv(normal_data.normalise_sum().alternatives, criteria, file)
    
    # Save "normalised vector" data to a csv file
    normal_data = NormalisedData(alternatives, criteria)
    file = output_folder / "normalised_vector.csv"
    write_list_of_alternatives_to_csv(normal_data.normalise_vector().alternatives, criteria, file)
    
    print(f" /n -----Normalised data saved to {output_folder}---- /n ")
    
@dataclass
class NormalisedData:
    """This class represents the normalised data for the alternatives and criteria."""
    alternatives: list[Alternative]
    criteria: list[Critere]
    _original_alternatives: list[Alternative] = field(default=None, init=False, repr=False)
    
    def __post_init__(self):
        """Store a deep copy of the original alternatives to preserve the original data."""
        if self._original_alternatives is None:
            self._original_alternatives = deepcopy(self.alternatives)    
    
    def normalise_max(self):
        """This method will normalise the values of all the alternatives following the formula: (v/max(V))"""
        for crit in self.criteria:
            max_value = max(alt.values[crit.name] for alt in alternatives)
            for alt in alternatives:
                if crit.direction == Direction.MAX:
                    alt.values[crit.name] = alt.values[crit.name] / max_value * 100 if max_value != 0 else 0
                else:
                    alt.values[crit.name] = (1 - alt.values[crit.name] / max_value) * 100 if max_value != 0 else 0
        self.alternatives = alternatives
        return self
    
    def normalise_max_min(self):
        """This method will normalise the values of all the alternatives following the formula: (v-min(V))/(max(V)-min(V))"""
        for crit in self.criteria:
            max_value = max(alt.values[crit.name] for alt in alternatives)
            min_value = min(alt.values[crit.name] for alt in alternatives)
            for alt in alternatives:
                if crit.direction == Direction.MAX:
                    alt.values[crit.name] = (alt.values[crit.name] - min_value) / (max_value - min_value) * 100 if max_value != min_value else 0
                else:
                    alt.values[crit.name] = (1 -(max_value - alt.values[crit.name]) / (max_value - min_value)) * 100 if max_value != min_value else 0
        self.alternatives = alternatives
        return self
    
    def normalise_sum(self):
        """This method will normalise following the formula v/sum(V)"""
        for crit in self.criteria:
            sum_value = sum(alt.values[crit.name] for alt in alternatives)
            for alt in alternatives:
                alt.values[crit.name] = alt.values[crit.name] / sum_value * 100 if sum_value != 0 else 0
        self.alternatives = alternatives
        return self
    
    def normalise_vector(self):
        """This method will normalise following the formula v/sqrt(sum(V^2))"""
        for crit in self.criteria:
            sum_squares = sum(alt.values[crit.name] ** 2 for alt in alternatives)
            norm = sum_squares ** 0.5
            for alt in alternatives:
                alt.values[crit.name] = alt.values[crit.name] / norm * 100 if norm != 0 else 0
        self.alternatives = alternatives
        return self
        

if __name__ == "__main__":
    # Filter the non-numeric, non-bare_minimum values from the criteria
    countries = ['Canada', 'Norway', 'Luxembourg', 'Switzerland', 'Sweden', 'Ireland']
    criteria = [crit for crit in load_criteria(Path(f"test/criteria.json")) if crit.type == "numeric" and crit.weight > 0 ]
    alternatives = [alt for alt in load_alternatives(Path(f"test/alternatives.csv")) if all(isinstance(alt.values[crit.name], (int, float)) and alt.name in countries for crit in criteria)]
    
    save_normalised_data(alternatives, criteria)
    