"""ELECTRE-style concordance analysis and visualisation."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import seaborn as sns

from domain import Alternative, Critere, Scenario
from loadData import load_criteria, load_alternatives, load_scenarios


def evaluate_alternatives(
    a: Alternative,
    b: Alternative,
    criteria: list[Critere],
    scenario: Scenario,
) -> tuple[float, float]:
    """Compare two alternatives and return their concordance scores.

    Scenario-level family weights are distributed across the criteria inside
    each family. The pairwise comparison then adds each criterion weight to the
    alternative that is better, or to both alternatives when their normalised
    values are close enough to be treated as equivalent.

    Args:
        a: First alternative.
        b: Second alternative.
        criteria: Criteria used in the comparison.
        scenario: Scenario defining family weights.

    Returns:
        A tuple ``(a_over_b, b_over_a)`` with the concordance score for each
        outranking direction.
    """

    concordance_1 = 0
    concordance_2 = 0
    final_weights = dict()
    
    # Convert family-level scenario weights into final criterion-level weights.
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

    # Values have already been normalised for ELECTRE, so larger is better.
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


def concordance_matrix(
    alternatives: list[Alternative],
    criteria: list[Critere],
    scenario: Scenario,
) -> pd.DataFrame:
    """Calculate pairwise concordance scores for every alternative pair.

    Args:
        alternatives: Alternatives to compare.
        criteria: Criteria used in the ELECTRE comparison.
        scenario: Scenario defining family weights.

    Returns:
        A square DataFrame indexed and columned by alternative name.
    """

    matrix = pd.DataFrame(
        index=[alt.name for alt in alternatives],
        columns=[alt.name for alt in alternatives],
    )

    for i, alt_a in enumerate(alternatives):
        for j, alt_b in enumerate(alternatives):
            if i != j:
                concordance1, concordance2 = evaluate_alternatives(
                    alt_a,
                    alt_b,
                    criteria,
                    scenario,
                )
                matrix.at[alt_a.name, alt_b.name] = concordance1
                matrix.at[alt_b.name, alt_a.name] = concordance2
            else:
                matrix.at[alt_a.name, alt_b.name] = 1  # No self-comparison

    return matrix


def heat_concordance_matrix(
    matrix: pd.DataFrame,
    scenario_name: str,
    output_folder: Path,
) -> None:
    """Save a heatmap view of a concordance matrix.

    Args:
        matrix: Concordance matrix to plot.
        scenario_name: Scenario name used in the output filename.
        output_folder: Folder where the PNG file will be saved.
    """

    output_folder.mkdir(exist_ok=True)

    plt.figure(figsize=(10, 8))
    sns.heatmap(matrix.astype(float), annot=True, cmap="YlGnBu", cbar=True)
    plt.title("Concordance Matrix")
    plt.xlabel("Alternative B")
    plt.ylabel("Alternative A")
    
    # Save the figure
    filepath = output_folder / f"heatmap_{scenario_name}.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    print(f"Heatmap saved to {filepath}")
    plt.close()


def graph_concordance_matrix(
    matrix: pd.DataFrame,
    seuil: float,
    scenario_name: str,
    output_folder: Path,
) -> None:
    """Save an outranking graph for concordance values above a threshold.

    Args:
        matrix: Concordance matrix to convert into graph edges.
        seuil: Minimum concordance score required to draw an edge.
        scenario_name: Scenario name used in the output filename.
        output_folder: Folder where the PNG file will be saved.
    """

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
                # Matrix cells can be empty when upstream data is incomplete.
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
    nx.draw_networkx_nodes(G, pos, node_color="lightblue", node_size=30)
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold")
    nx.draw_networkx_edges(
        G,
        pos,
        edge_color="gray",
        width=2,
        arrows=True,
        arrowsize=70,
        arrowstyle="->",
        connectionstyle="arc3,rad=0.1",
    )
    plt.title("Concordance Graph", fontsize=14)
    plt.axis("off")
    plt.tight_layout()

    # Save the figure
    filepath = output_folder / f"outranking_graph_{scenario_name}.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    print(f"Outranking graph saved to {filepath}")
    plt.close()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for ELECTRE analysis.

    Returns:
        Parsed CLI arguments.
    """

    parser = argparse.ArgumentParser(
        description="Run ELECTRE concordance analysis for MCDA alternatives."
    )
    parser.add_argument(
        "--normalised_data",
        type=Path,
        help="Folder containing ELECTRE-normalised alternatives.",
    )
    parser.add_argument("--criteria", type=Path)
    parser.add_argument("--alternatives", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--scenarios", type=Path)
    parser.add_argument("--threshold", type=float)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    criteria = load_criteria(args.criteria)
    scenarios = load_scenarios(args.scenarios)

    # Create output folder
    if args.output is not None:
        args.output.mkdir(parents=True, exist_ok=True)
        results_file = args.output / "electra_results.txt"

    # Each scenario reads the matching ELECTRE-normalised alternatives file.
    first_scenario = True
    for scenario in scenarios:
        print(f"Scenario: {scenario.name} : description: {scenario.description}")
        alternative_file = args.normalised_data / f"normalised_electre_{scenario.name}.csv"
        alternatives = load_alternatives(alternative_file)
        if args.output is not None:
            matrix = concordance_matrix(alternatives, criteria, scenario)

            # Overwrite for the first scenario, then append the remaining ones.
            mode = "w" if first_scenario else "a"
            with open(results_file, mode) as f:
                f.write(f"Scenario: {scenario.name} : description: {scenario.description}\n")
                df = pd.DataFrame(matrix)
                df.to_csv(f, index=False)
                f.write("\n")

            heat_concordance_matrix(matrix, scenario.name, output_folder=args.output)
            graph_concordance_matrix(
                matrix,
                seuil=args.threshold,
                scenario_name=scenario.name,
                output_folder=args.output,
            )
            print(f"Results saved to {args.output}")
            first_scenario = False
        else:
            print("No output file specified. Skipping save.")
