#This code will load a json file to identify the criteria and then a csv file to load the numeric values 

import json
import csv
import numpy as np
from pathlib import Path
from domain import Critere, Alternative, Scenario, Direction

def load_criteria(file: Path) -> list[Critere]:
    with open(file, 'r') as f:
        data = json.load(f)
    criteria_list = []
    for item in data['Criteria']:
        criterion = Critere(
            name=item['name'],
            direction=Direction(item['direction']),
            type=item['type'],
            weight=item['weight'],
            threshold=item.get('threshold', 0.0),
            bare_minimum=item.get('bare_minimum', 0.0),
            categories=item.get('categories'),
            family=item.get('family')
        )
        criteria_list.append(criterion)
    return criteria_list

def load_alternatives(file: Path) -> list[Alternative]:
    alternatives = []
    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            alt = Alternative(
                name=row['Name'],
                values={k: float(v) if v.replace('.','',1).isdigit() else v for k, v in row.items() if k != 'Name'}
            )
            alternatives.append(alt)
    return alternatives

if __name__ == "__main__":
    criteria = load_criteria(Path("test/criteria.json"))
    print("\nLoaded Criteria:")
    for crit in criteria:
        print(crit.name)
    print("\nLoaded Alternatives:")
    alternatives = load_alternatives(Path("test/alternatives.csv"))
    for alt in alternatives:
        print(alt.name)
