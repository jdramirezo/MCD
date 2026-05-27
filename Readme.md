# AMCD / MCDA Decision Analysis Toolkit

This repository contains a small multi-criteria decision analysis toolkit. It can:

- filter alternatives with satisfaction constraints;
- reduce alternatives with dominance analysis;
- normalise criteria values with several methods;
- compute scenario-based weighted scores;
- run ELECTRE-style pairwise outranking;
- generate Docker report artifacts, including CSV files, concordance matrices, heatmaps, and outranking graphs.

The easiest and most reproducible way to use the project is through `docker_report.sh`.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `docker_report.sh` | Main Docker workflow. Builds a temporary image, runs all AMCD steps, and writes report artifacts. |
| `docker_report_cars.inputs` | Input configuration for the car example. |
| `docker_report_countries.inputs` | Input configuration for the country example. |
| `python-core/amcd-core/` | Python implementation of satisfaction, dominance, normalisation, weighted scoring, and ELECTRE. |
| `exemples/cars/` | Example car alternatives, criteria, and scenarios. |
| `exemples/countries/` | Example country alternatives, criteria, and scenarios. |
| `exemples/docker-report-*` | Example generated outputs. |
| `.github/agents/MCD_agent.md` | Reporting-agent instructions for turning generated artifacts into a narrative `AMCD_report.md`. |

## Prerequisites

For the Docker workflow:

- Docker Desktop or a running Docker daemon;
- a POSIX shell such as `bash` or `zsh`;
- network access during the first Docker build, unless the image layers are already cached.

For local Python usage:

- Python 3.12 recommended;
- dependencies from `python-core/pyproject.toml`.

## Quick Start With Docker

Run the car example:

```bash
./docker_report.sh \
  --input-config docker_report_cars.inputs \
  --output docker-report-cars \
  --family pere_de_famille \
  --threshold 0.8
```

Run the country example:

```bash
./docker_report.sh \
  --input-config docker_report_countries.inputs \
  --output docker-report-countries \
  --family economic \
  --threshold 0.7
```

The script expects an input configuration file defining:

```bash
CRITERIA_FILE="path/to/criteria.json"
ALTERNATIVES_FILE="path/to/alternatives.csv"
SCENARIOS_FILE="path/to/scenarios.json"
```

Paths may be absolute or relative to the input configuration file.

## Docker Workflow Options

```bash
./docker_report.sh [options]
```

| Option | Description |
| --- | --- |
| `-o, --output DIR` | Folder where generated artifacts are written. |
| `-c, --input-config FILE` | Input config defining criteria, alternatives, and scenarios. |
| `-f, --family FAMILY` | Criteria family used for satisfaction and dominance. Use quotes for several families, for example `"economic life"`. |
| `-t, --threshold VALUE` | ELECTRE concordance threshold. |
| `--pip-config FILE` | Pip config to use during Docker build, useful behind a proxy or private index. |
| `--no-cache` | Rebuild the Docker image without cache. |
| `--keep-image` | Keep the generated Docker image after the run. |
| `-h, --help` | Show script help. |

Note: the script default input name is `docker_report.inputs`, but this repository currently provides `docker_report_cars.inputs` and `docker_report_countries.inputs`. Pass `--input-config` explicitly unless you add your own `docker_report.inputs`.

## Generated Artifacts

Each Docker run writes files into the selected output directory:

| Artifact | Meaning |
| --- | --- |
| `README.md` | Short machine-generated summary of the run parameters and outputs. |
| `docker_report.log` | Full execution log. Useful for inspecting dominance explanations and command output. |
| `satisfaction.csv` | Alternatives retained and eliminated by the satisfaction step. |
| `dominance.csv` | Non-dominated alternatives retained for normalisation and scoring. |
| `normalised/normalised_max.csv` | Values normalised against each criterion maximum. |
| `normalised/normalised_max_min.csv` | Values normalised between each criterion minimum and maximum. |
| `normalised/normalised_sum.csv` | Values normalised as shares of each criterion total. |
| `normalised/normalised_vector.csv` | Values normalised with vector scaling. |
| `normalised/normalised_electre_*.csv` | Scenario-specific normalised inputs for ELECTRE. |
| `weights_results.csv` | Weighted scores by scenario and normalisation method. |
| `electra/electra_results.txt` | ELECTRE concordance matrices. |
| `electra/heatmap_*.png` | Heatmaps of concordance matrices. |
| `electra/outranking_graph_*.png` | Directed outranking graphs after applying the threshold. |

The Docker workflow generates analysis artifacts. To produce a full narrative report, use the instructions in `.github/agents/MCD_agent.md` and write the final Markdown file as `<output-directory>/AMCD_report.md`.

## Creating a Narrative Report With the MCD Agent

The Docker workflow creates the raw decision-analysis artifacts. A readable
decision report is a second step: it should inspect the generated CSV files,
normalisation outputs, ELECTRE matrices, heatmaps, and outranking graphs, then
write a human-oriented `AMCD_report.md`.

This repository includes an agent specification for that task:

```text
.github/agents/MCD_agent.md
```

Use the MCD Report agent after Docker has generated the artifacts, or ask it to
run Docker and then write the report. The final report should be written inside
the selected Docker output directory:

```text
<output-directory>/AMCD_report.md
```

Example prompt for the car study:

```text
Use the MCD Report agent to run the AMCD Docker workflow and generate a complete
AMCD_report.md. Use docker_report_cars.inputs as the input config and
docker-report-cars as the output directory. Use pere_de_famille as the family
for the Docker command and 0.8 as the ELECTRE threshold. After Docker finishes,
inspect all generated artifacts and write a readable report with detailed
interpretation of the satisfaction, dominance, weighted score, normalisation,
and ELECTRE results. When treating the ELECTRE results, interpret each heatmap
and outranking graph so the reader can understand its meaning.
```

The generated report should normally include:

- an executive summary;
- the purpose of the study;
- input files, alternatives, criteria, and scenarios;
- satisfaction and dominance interpretation;
- normalisation and weighted-score interpretation;
- ELECTRE interpretation with links to every heatmap and graph;
- scenario sensitivity;
- final decision-oriented conclusions;
- limitations and assumptions;
- an artifact index.

## Input Data Format

### Alternatives CSV

The alternatives file is a CSV table. It must contain a `name` column plus one column per criterion.

Example:

```csv
name,Reliability Score (/100),Boot Volume (L),Power (hp)
Example Car A,82,328,100
Example Car B,92,397,116
```

Criterion column names must match the `name` values in `criteria.json`.

### Criteria JSON

The criteria file contains a `Criteria` array. Each criterion defines how values are interpreted.

```json
{
  "Criteria": [
    {
      "name": "Reliability Score (/100)",
      "direction": "max",
      "description": "Higher is better.",
      "type": "numeric",
      "weight": 1,
      "threshold": 5,
      "bare_minimum": 70,
      "family": "pere_de_famille"
    }
  ]
}
```

Important fields:

| Field | Meaning |
| --- | --- |
| `name` | Must match a column in the alternatives CSV. |
| `direction` | `max` means higher is better; `min` means lower is better. |
| `type` | Current workflow expects numeric criteria. |
| `weight` | Base weight inside its family. |
| `threshold` | Indifference or comparison threshold used by dominance/ELECTRE-related logic. |
| `bare_minimum` | Minimum viability level used by satisfaction. |
| `family` | Group used for scenario weighting and satisfaction/dominance filtering. |

### Scenarios JSON

The scenarios file contains a `Scenarios` array. Each scenario assigns weights to criterion families.

```json
{
  "Scenarios": [
    {
      "name": "equal_weights",
      "description": "Equal weight for both families.",
      "weights": {
        "pere_de_famille": 0.5,
        "toreto": 0.5
      }
    }
  ]
}
```

Scenario family names must match the `family` values in `criteria.json`.

## Notes and Limitations

- Satisfaction and dominance only use the family or families passed with `--family`.
- Weighted scoring and ELECTRE use the scenario family weights.
- Results are sensitive to criterion directions, thresholds, bare minimums, and scenario weights.
- The generated Docker image is removed after the run unless `--keep-image` is passed.
- The output directory may be overwritten or updated by repeated runs with the same path.
- The current code is research/prototype oriented; review outputs before using them for high-stakes decisions.
