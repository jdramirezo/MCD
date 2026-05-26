# AMCD Docker Report

Generated inside Docker.

## Parameters

- Family: `pere_de_famille`
- ELECTRE threshold: `0.7`
- Criteria file: `/app/input/criteria.json`
- Alternatives file: `/app/input/alternatives.csv`
- Scenarios file: `/app/input/scenarios.json`

## Files

- `satisfaction.csv`: retained alternatives after satisfaction filtering
- `dominance.csv`: non-dominated alternatives
- `normalised/`: normalised CSV files
- `weights_results.csv`: weighted mean results
- `electra/electra_results.txt`: ELECTRE concordance matrices
- `electra/*.png`: heatmaps and outranking graphs
- `docker_report.log`: full Docker execution log
