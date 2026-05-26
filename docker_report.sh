#!/usr/bin/env bash
set -euo pipefail

# Get the directory of this script
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
PROJECT_ROOT="$SCRIPT_DIR"
PYTHON_CORE="$PROJECT_ROOT/python-core"
AMCD_CORE="$PYTHON_CORE/amcd-core"

# Docker image settings
IMAGE_NAME="amcd-report"
IMAGE_TAG="latest"

# Default parameters
OUTPUT_DIR="$PROJECT_ROOT/docker-report"
FAMILY="economic"
THRESHOLD="0.5"
NO_CACHE="false"
KEEP_IMAGE="false"
PIP_CONFIG_FILE="${PIP_CONFIG_FILE:-}"

# Print usage/help message
usage() {
    cat <<EOF
AMCD Docker Report

Usage: ./docker_report.sh [options]

Options:
  -o, --output DIR       Folder where report files are written (default: ./docker-report)
  -f, --family FAMILY    Criteria family for satisfaction/dominance (default: economic)
                         Repeat or quote values for multiple families, e.g. "economic life"
  -t, --threshold VALUE  ELECTRE concordance threshold (default: 0.5)
      --pip-config FILE  Pip config to use during Docker build (pip.conf or pip.ini)
      --no-cache         Build the Docker image without cache
      --keep-image       Do not remove the generated Docker image at the end
  -h, --help             Show this help

Examples:
  ./docker_report.sh
  ./docker_report.sh --family "economic life" --threshold 0.6
  ./docker_report.sh --output ./reports/amcd
    ./docker_report.sh --pip-config ~/.config/pip/pip.conf
EOF
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -f|--family)
            FAMILY="$2"
            shift 2
            ;;
        -t|--threshold)
            THRESHOLD="$2"
            shift 2
            ;;
        --pip-config)
            PIP_CONFIG_FILE="$2"
            shift 2
            ;;
        --no-cache)
            NO_CACHE="true"
            shift
            ;;
        --keep-image)
            KEEP_IMAGE="true"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "❌ Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Convert a path for Docker mounting (handles Windows/cygwin)
docker_path() {
    local path="$1"
    if command -v cygpath >/dev/null 2>&1; then
        cygpath -m "$path"
    else
        printf '%s' "$path"
    fi
}

# Try to find a pip config file for use in Docker build
find_pip_config() {
    local candidates=()

    # If user specified, try that first
    if [[ -n "${PIP_CONFIG_FILE:-}" ]]; then
        candidates+=("$PIP_CONFIG_FILE")
    fi

    # Common pip config locations
    candidates+=(
        "$HOME/.config/pip/pip.conf"
        "$HOME/.pip/pip.conf"
        "$HOME/pip/pip.ini"
    )

    # Try Windows pip.ini if running in WSL
    if command -v python.exe >/dev/null 2>&1; then
        local windows_appdata
        windows_appdata=$(python.exe -c "import os; print(os.environ.get('APPDATA', ''))" 2>/dev/null | tr -d '\r')
        if [[ -n "$windows_appdata" ]] && command -v wslpath >/dev/null 2>&1; then
            candidates+=("$(wslpath -u "$windows_appdata")/pip/pip.ini")
        fi
    fi

    # Return the first file found
    for candidate in "${candidates[@]}"; do
        if [[ -f "$candidate" ]]; then
            printf '%s' "$candidate"
            return 0
        fi
    done

    return 1
}

# Cleanup temp files and Docker image if needed
cleanup() {
    if [[ -n "${TMP_DIR:-}" && -d "$TMP_DIR" ]]; then
        rm -rf "$TMP_DIR"
    fi
    if [[ "$KEEP_IMAGE" != "true" ]]; then
        docker rmi "$IMAGE_NAME:$IMAGE_TAG" >/dev/null 2>&1 || true
    fi
}
trap cleanup EXIT

# Print summary of settings
echo "🐳 AMCD Docker Report"
echo "====================="
echo "> PROJECT_ROOT: $PROJECT_ROOT"
echo "> AMCD_CORE:    $AMCD_CORE"
echo "> OUTPUT_DIR:   $OUTPUT_DIR"
echo "> FAMILY:       $FAMILY"
echo "> THRESHOLD:    $THRESHOLD"
echo

# Check Docker is installed and running
if ! command -v docker >/dev/null 2>&1; then
    echo "❌ Docker is not installed or not available in PATH."
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Start Docker Desktop and retry."
    exit 1
fi

# Check all required files exist
for required_file in \
    "$AMCD_CORE/domain.py" \
    "$AMCD_CORE/loadData.py" \
    "$AMCD_CORE/satisfaction.py" \
    "$AMCD_CORE/dominance.py" \
    "$AMCD_CORE/normalize.py" \
    "$AMCD_CORE/weights.py" \
    "$AMCD_CORE/electra.py" \
    "$AMCD_CORE/test/criteria.json" \
    "$AMCD_CORE/test/alternatives.csv" \
    "$AMCD_CORE/test/scenarios.json"; do
    if [[ ! -f "$required_file" ]]; then
        echo "❌ Missing required file: $required_file"
        exit 1
    fi
done

# Prepare output and temp directories
mkdir -p "$OUTPUT_DIR"
OUTPUT_DIR=$(cd "$OUTPUT_DIR" && pwd)
TMP_DIR=$(mktemp -d -t amcd-docker-report-XXXXXX)

echo "✅ Preparing Docker build context"
cp -R "$AMCD_CORE" "$TMP_DIR/amcd-core"

# Find pip config if available
if PIP_CONFIG_FILE=$(find_pip_config); then
    echo "✅ Using pip config during Docker build: $PIP_CONFIG_FILE"
    USE_PIP_CONFIG="true"
else
    echo "⚠️  No pip config found. Use --pip-config /path/to/pip.conf if pip needs a proxy/index."
    USE_PIP_CONFIG="false"
fi

# Write Dockerfile to temp dir, using pip config if found
if [[ "$USE_PIP_CONFIG" == "true" ]]; then
    cat > "$TMP_DIR/Dockerfile" <<'EOF'
# syntax=docker/dockerfile:1.4
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg

WORKDIR /app

# Use pip config as a secret for proxy/index
RUN --mount=type=secret,id=pip_config,target=/etc/pip.conf \
    pip install --no-cache-dir \
    "requests" \
    "pandas" \
    "numpy" \
    "networkx" \
    "matplotlib" \
    "seaborn"

COPY amcd-core /app/amcd-core
COPY run_amcd_report.sh /usr/local/bin/run_amcd_report.sh

RUN chmod +x /usr/local/bin/run_amcd_report.sh

ENTRYPOINT ["/usr/local/bin/run_amcd_report.sh"]
EOF
else
    cat > "$TMP_DIR/Dockerfile" <<'EOF'
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg

WORKDIR /app

RUN pip install --no-cache-dir \
    "requests" \
    "pandas" \
    "numpy" \
    "networkx" \
    "matplotlib" \
    "seaborn"

COPY amcd-core /app/amcd-core
COPY run_amcd_report.sh /usr/local/bin/run_amcd_report.sh

RUN chmod +x /usr/local/bin/run_amcd_report.sh

ENTRYPOINT ["/usr/local/bin/run_amcd_report.sh"]
EOF
fi

# Write the script that runs inside the container
cat > "$TMP_DIR/run_amcd_report.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

# Read parameters from environment variables
FAMILY=${AMCD_FAMILY:-economic}
THRESHOLD=${AMCD_THRESHOLD:-0.5}
REPORT_DIR=/report
NORMALISED_DIR="$REPORT_DIR/normalised"
ELECTRA_DIR="$REPORT_DIR/electra"

mkdir -p "$NORMALISED_DIR" "$ELECTRA_DIR"
cd /app/amcd-core

# Helper to time and log each step
run_step() {
    local name="$1"
    shift

    echo
    echo "▶ $name"
    local start
    local end
    start=$(date +%s)
    "$@"
    end=$(date +%s)
    echo "✅ $name completed in $((end - start))s"
}

echo "🐍 Python: $(python --version 2>&1)"
echo "📁 Report directory: $REPORT_DIR"
echo "🏷️ Families: $FAMILY"
echo "📏 ELECTRE threshold: $THRESHOLD"

# shellcheck disable=SC2206
FAMILY_ARGS=($FAMILY)

# Run each analysis step, outputting to the report directory
run_step "Satisfaction analysis" \
    python satisfaction.py \
        --criteria test/criteria.json \
        --alternatives test/alternatives.csv \
        --family "${FAMILY_ARGS[@]}" \
        --output "$REPORT_DIR/satisfaction.csv"

run_step "Dominance analysis" \
    python dominance.py \
        --satisfaction_output "$REPORT_DIR/satisfaction.csv" \
        --criteria test/criteria.json \
        --alternatives test/alternatives.csv \
        --family "${FAMILY_ARGS[@]}" \
        --output "$REPORT_DIR/dominance.csv"

run_step "Normalisation" \
    python normalize.py \
        --dominance_output "$REPORT_DIR/dominance.csv" \
        --criteria test/criteria.json \
        --alternatives test/alternatives.csv \
        --scenarios test/scenarios.json \
        --output "$NORMALISED_DIR"

run_step "Weighted means" \
    python weights.py \
        --normalised_data "$NORMALISED_DIR" \
        --criteria test/criteria.json \
        --alternatives test/alternatives.csv \
        --scenarios test/scenarios.json \
        --output "$REPORT_DIR/weights_results.csv"

run_step "ELECTRE analysis" \
    python electra.py \
        --normalised_data "$NORMALISED_DIR" \
        --criteria test/criteria.json \
        --scenarios test/scenarios.json \
        --threshold "$THRESHOLD" \
        --output "$ELECTRA_DIR"

# Write a summary README in the output
cat > "$REPORT_DIR/README.md" <<REPORT
# AMCD Docker Report

Generated inside Docker.

## Parameters

- Family: \`$FAMILY\`
- ELECTRE threshold: \`$THRESHOLD\`

## Files

- \`satisfaction.csv\`: retained alternatives after satisfaction filtering
- \`dominance.csv\`: non-dominated alternatives
- \`normalised/\`: normalised CSV files
- \`weights_results.csv\`: weighted mean results
- \`electra/electra_results.txt\`: ELECTRE concordance matrices
- \`electra/*.png\`: heatmaps and outranking graphs
- \`docker_report.log\`: full Docker execution log
REPORT

echo
echo "📋 Generated files:"
find "$REPORT_DIR" -maxdepth 2 -type f | sort
echo
echo "✅ AMCD Docker report completed"
EOF

# Build the Docker image, using pip config as a secret if available
echo "🔨 Building Docker image: $IMAGE_NAME:$IMAGE_TAG"
BUILD_ARGS=(-f "$TMP_DIR/Dockerfile" -t "$IMAGE_NAME:$IMAGE_TAG")
if [[ "$NO_CACHE" == "true" ]]; then
    BUILD_ARGS+=(--no-cache)
fi
if [[ "$USE_PIP_CONFIG" == "true" ]]; then
    BUILD_ARGS+=(--secret "id=pip_config,src=$PIP_CONFIG_FILE")
fi
BUILD_ARGS+=("$TMP_DIR")
DOCKER_BUILDKIT=1 docker build "${BUILD_ARGS[@]}"

# Run the container, mounting the output directory
echo
echo "🚀 Running AMCD report container"
DOCKER_OUTPUT_DIR=$(docker_path "$OUTPUT_DIR")
docker run --rm \
    --memory=1g \
    --cpus=1.0 \
    -e AMCD_FAMILY="$FAMILY" \
    -e AMCD_THRESHOLD="$THRESHOLD" \
    -v "$DOCKER_OUTPUT_DIR:/report" \
    "$IMAGE_NAME:$IMAGE_TAG" | tee "$OUTPUT_DIR/docker_report.log"

# Print a summary table
echo
echo "📊 Report summary"
echo "┌──────────────────────┬────────────────────────────────────────┐"
printf "│ %-20s │ %-38s │\n" "Output folder" "$OUTPUT_DIR"
printf "│ %-20s │ %-38s │\n" "Log file" "docker_report.log"
printf "│ %-20s │ %-38s │\n" "ELECTRE folder" "electra"
echo "└──────────────────────┴────────────────────────────────────────┘"

echo
echo "✅ Done. Open $OUTPUT_DIR/README.md for the generated report index."