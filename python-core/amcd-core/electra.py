import pandas as pd

from loadData import load_criteria, load_alternatives, load_scenarios
from domain import Critere, Alternative, Direction, Scenario
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

def evaluate_alternatives(a: Alternative, b: Alternative, criteria: list[Critere], scenario: Scenario) -> tuple[float, float]:
    """Evaluate two alternatives following the ELECTRE method."""
    concordance_1 = 0
    concordance_2 = 0
    final_weights = dict()
    
    for family in scenario.weights:
        family_weight = scenario.weights[family]
        family_weights = [crit.weight * family_weight / sum(crit.weight for crit in criteria if crit.family == family) for crit in criteria]
        for crit in criteria:
            if crit.family == family:
                final_weights[crit.name] = family_weights[criteria.index(crit)]
    
    for crit in criteria:
        weight = final_weights.get(crit.name, 0)
        diff = a.values.get(crit.name, 0) - b.values.get(crit.name, 0)
        if diff > 1:
            concordance_1 += weight
        elif diff < -1:
            concordance_2 += weight
        else:
            concordance_1 += weight 
            concordance_2 += weight 

    return concordance_1, concordance_2

def concordance_matrix(alternatives: list[Alternative], criteria: list[Critere], scenario: Scenario) -> pd.DataFrame:
    """Calculate the concordance matrix for a list of alternatives."""
    matrix = pd.DataFrame(index=[alt.name for alt in alternatives], columns=[alt.name for alt in alternatives])
    
    for i, alt_a in enumerate(alternatives):
        for j, alt_b in enumerate(alternatives):
            if i != j:
                concordance1, concordance2 = evaluate_alternatives(alt_a, alt_b, criteria, scenario)
                matrix.at[alt_a.name, alt_b.name] = concordance1
                matrix.at[alt_b.name, alt_a.name] = concordance2
            else:
                matrix.at[alt_a.name, alt_b.name] = None  # No self-comparison

    return matrix

def heat_concordance_matrix(matrix: pd.DataFrame, scenario_name: str):
    """Draw the concordance matrix using matplotlib and save as PNG."""
    # Create output folder if it doesn't exist
    output_folder = Path("outranking graphs")
    output_folder.mkdir(exist_ok=True)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(matrix.astype(float), annot=True, cmap="YlGnBu", cbar=True)
    plt.title("Concordance Matrix")
    plt.xlabel("Alternative B")
    plt.ylabel("Alternative A")
    
    # Save the figure
    filepath = output_folder / f"heatmap_{scenario_name}.png"
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"Heatmap saved to {filepath}")
    plt.close()
    
def graph_concordance_matrix(matrix: pd.DataFrame, seuil: float, scenario_name):
    """Graph the concordance matrix as a directed graph and save as PNG."""
    import networkx as nx
    
    # Create output folder if it doesn't exist
    output_folder = Path("outranking graphs")
    output_folder.mkdir(exist_ok=True)
    
    G = nx.DiGraph()
    
    # Add all nodes first
    for alt in matrix.index:
        G.add_node(alt)
    
    # Add edges where concordance exceeds threshold
    for alt_a in matrix.index:
        for alt_b in matrix.columns:
            if alt_a != alt_b:
                concordance_a_b = matrix.at[alt_a, alt_b]
                # Skip None and NaN values
                if concordance_a_b is not None and pd.notna(concordance_a_b):
                    if float(concordance_a_b) > seuil:
                        G.add_edge(alt_a, alt_b, weight=float(concordance_a_b))
    
    # Debug: Print graph info
    print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    if G.number_of_edges() == 0:
        print(f"Warning: No edges with concordance > {seuil}")
        return
    
    pos = nx.spring_layout(G, seed=42, k=2)
    
    plt.figure(figsize=(12, 10))
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=3000)
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')
    nx.draw_networkx_edges(G, pos, edge_color='gray', width=2, arrows=True, 
                          arrowsize=50, arrowstyle='->', connectionstyle='arc3,rad=0.1')
    plt.title("Concordance Graph", fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    
    # Save the figure
    filepath = output_folder / f"outranking_graph_{scenario_name}.png"
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"Outranking graph saved to {filepath}")
    plt.close()
    
if __name__ == "__main__":
    countries = ['Canada', 'Norway', 'Luxembourg', 'Switzerland', 'Sweden', 'Ireland']
    criteria = [crit for crit in load_criteria(Path(f"test/criteria.json")) if crit.type == "numeric" and crit.weight > 0 ]
    alternatives_max = [alt for alt in load_alternatives(Path(f"test/normalised_data/normalised_electre_equal_weights.csv")) if all(isinstance(alt.values[crit.name], (int, float)) and alt.name in countries for crit in criteria)]
    scenarios = load_scenarios(Path(f"test/scenarios.json"))
    
    concordance = concordance_matrix(alternatives_max, criteria, scenarios[0])
    
    print("Concordance Matrix:")
    
    print(concordance)
    
    scenario_name = scenarios[0].name
    heat_concordance_matrix(concordance, scenario_name)
    graph_concordance_matrix(concordance, seuil=0.7, scenario_name=scenario_name)