#!/bin/bash
#
# Shell wrapper for running benchmarks in ACTIVATE workflow.
# This script is called by the workflow and invokes the Python benchmark module.
#

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Set default values from environment or use defaults
DURATION="${DURATION:-10}"
RUN_CPU="${RUN_CPU:-true}"
RUN_MEMORY="${RUN_MEMORY:-true}"
RUN_DISK="${RUN_DISK:-true}"
OUTPUT_DIR="${JOB_DIR:-$PROJECT_DIR/results}"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "Single Node Benchmark"
echo "=========================================="
echo "Duration per test: ${DURATION}s"
echo "Run CPU test: $RUN_CPU"
echo "Run Memory test: $RUN_MEMORY"
echo "Run Disk I/O test: $RUN_DISK"
echo "Output directory: $OUTPUT_DIR"
echo "=========================================="
echo ""

# Run Python benchmark module
cd "$PROJECT_DIR"
python3 -c "
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, '.')
from scripts.run_benchmarks import run_all_benchmarks, get_system_info

duration = int(os.environ.get('DURATION', 10))
run_cpu = os.environ.get('RUN_CPU', 'true').lower() == 'true'
run_memory = os.environ.get('RUN_MEMORY', 'true').lower() == 'true'
run_disk = os.environ.get('RUN_DISK', 'true').lower() == 'true'
output_dir = os.environ.get('JOB_DIR', './results')

# Collect system info
system_info = get_system_info()
print(f\"System: {system_info['hostname']}\")
print(f\"CPUs: {system_info['cpu_count']}, Memory: {system_info['memory_gb']:.1f} GB\")
print()

# Run benchmarks
benchmarks = run_all_benchmarks(
    duration=duration,
    run_cpu=run_cpu,
    run_memory=run_memory,
    run_disk=run_disk
)

# Assemble results
results = {
    'timestamp': datetime.utcnow().isoformat() + 'Z',
    'system_info': system_info,
    'benchmarks': benchmarks
}

# Save results
results_file = os.path.join(output_dir, 'benchmark_results.json')
with open(results_file, 'w') as f:
    json.dump(results, f, indent=2)

print()
print(f'Results saved to: {results_file}')
print(f'RESULTS_FILE={results_file}')
"

# Output the results file path for ACTIVATE workflow
RESULTS_FILE="$OUTPUT_DIR/benchmark_results.json"
echo "RESULTS_FILE=$RESULTS_FILE" >> "${OUTPUTS:-/dev/null}"

echo ""
echo "Benchmark complete!"
