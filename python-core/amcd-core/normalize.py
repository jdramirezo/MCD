from domain import Critere, Alternative
from loadData import load_criteria, load_alternatives
from dataclasses import dataclass
from pathlib import Path
import csv


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


@dataclass
class NormalisedData:
    """This class represents the normalised data for the alternatives and criteria."""
    alternatives: list[Alternative]
    criteria: list[Critere]
    
    def set_to_maximise(self):
        """This method will modify the values of all the alternatives for the given criterion to be maximised. If a criterion is to be minimised, we will transform it to be maximised by taking the inverse of the values."""
        for crit in self.criteria:
            max_value = max(alt.values[crit.name] for alt in self.alternatives)
            if crit.direction == "min":
                for alt in self.alternatives:
                    alt.values[crit.name] = max_value - alt.values[crit.name]
        return self
    
    def normalise_max(self):
        """This method will normalise the values of all the alternatives following the formula: (v/max(V))"""
        alternatives = self.set_to_maximise().alternatives
        for crit in self.criteria:
            max_value = max(alt.values[crit.name] for alt in alternatives)
            for alt in alternatives:
                alt.values[crit.name] = alt.values[crit.name] / max_value if max_value != 0 else 0
        return self
    
    def normalise_max_min(self):
        """This method will normalise the values of all the alternatives following the formula: (v-min(V))/(max(V)-min(V))"""
        alternatives = self.set_to_maximise().alternatives
        for crit in self.criteria:
            max_value = max(alt.values[crit.name] for alt in alternatives)
            min_value = min(alt.values[crit.name] for alt in alternatives)
            for alt in alternatives:
                alt.values[crit.name] = (alt.values[crit.name] - min_value) / (max_value - min_value) if max_value != min_value else 0
        return self
    def normalise_sum(self):
        """This method will normalise following the formula v/sum(V)"""
        alternatives = self.set_to_maximise().alternatives
        for crit in self.criteria:
            sum_value = sum(alt.values[crit.name] for alt in alternatives)
            for alt in alternatives:
                alt.values[crit.name] = alt.values[crit.name] / sum_value if sum_value != 0 else 0
        return self
    
    def normalise_vector(self):
        """This method will normalise following the formula v/sqrt(sum(V^2))"""
        alternatives = self.set_to_maximise().alternatives
        for crit in self.criteria:
            sum_squares = sum(alt.values[crit.name] ** 2 for alt in alternatives)
            norm = sum_squares ** 0.5
            for alt in alternatives:
                alt.values[crit.name] = alt.values[crit.name] / norm if norm != 0 else 0
        return self
        

if __name__ == "__main__":
    # Filter the non-numeric, non-bare_minimum values from the criteria
    criteria = [crit for crit in load_criteria(Path(f"test/criteria.json")) if crit.type == "numeric" and crit.weight > 0 ]
    alternatives = [alt for alt in load_alternatives(Path(f"test/alternatives.csv")) if all(isinstance(alt.values[crit.name], (int, float)) for crit in criteria)]
    normalised_data = NormalisedData(alternatives, criteria)
    
    print("data set to maximise:")
    normalised_data.set_to_maximise()
    print(format_markdown_table(normalised_data.alternatives, normalised_data.criteria))
    
    print("Normalised data (table):")
    normalised_data.normalise_max()
    print(format_markdown_table(normalised_data.alternatives, criteria))