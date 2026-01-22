# Single Node Benchmark Workflow

System benchmarking workflow for the Parallel Works ACTIVATE platform. Runs CPU, memory, and disk I/O benchmarks on a single node and displays results through an interactive Plotly-based web visualization.

## Quick Start

### Run Locally

```bash
pip install -r requirements.txt
python scripts/local_runner.py --duration 10
```

### Deploy to ACTIVATE

1. Push this repository to your ACTIVATE account
2. Select the workflow from your workflows list
3. Configure benchmark options and target cluster
4. Run and view interactive results via the tunnel session

## Workflow Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| cluster | compute-clusters | - | Target cluster for benchmark execution |
| duration | number | 10 | Duration for each benchmark in seconds (5-60) |
| run_cpu | boolean | true | Run CPU benchmark |
| run_memory | boolean | true | Run memory benchmark |
| run_disk | boolean | true | Run disk I/O benchmark |

## Benchmarks

| Benchmark | Metric | Description |
|-----------|--------|-------------|
| CPU | ops/sec | Prime number calculations measuring single-thread performance |
| Memory | MB/s | Sequential memory read/write throughput |
| Disk I/O | MB/s | Sequential file read/write using 256MB test file |

### CPU Benchmark

Calculates prime numbers using trial division. Measures operations per second and tracks the number of primes found during the test duration.

### Memory Benchmark

Allocates a 100MB buffer and performs sequential write and read operations. Measures throughput in MB/s for both operations.

### Disk I/O Benchmark

Uses `dd` to write a 256MB test file and then read it back. Measures sequential throughput in MB/s. The test file is automatically cleaned up after the benchmark.

## Results

Benchmark results are saved as:
- `benchmark_results.json` - Raw results in JSON format
- `benchmark_results.html` - Interactive Plotly visualization

The HTML visualization includes:
- Bar charts for each benchmark type
- System information table
- Hover tooltips with detailed metrics

## Development

### Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scripts --cov-report=html

# Skip slow integration tests
pytest -m "not slow"
```

### Local Runner Options

```bash
# Quick test with short duration
python scripts/local_runner.py --duration 3

# Run only CPU benchmark
python scripts/local_runner.py --cpu-only --duration 5

# Run and serve results in browser
python scripts/local_runner.py --duration 10 --serve

# Specify custom output directory
python scripts/local_runner.py --output-dir ./my_results --serve --port 9000
```

## Project Structure

```
activate-benchmark/
├── workflow.yaml           # ACTIVATE workflow definition
├── scripts/
│   ├── __init__.py         # Package marker
│   ├── run_benchmarks.sh   # Benchmark execution script
│   ├── run_benchmarks.py   # Python module for benchmarks (testable)
│   ├── generate_plot.py    # Interactive plot generation (Plotly)
│   ├── serve_results.py    # Simple HTTP server for results
│   └── local_runner.py     # CLI tool to run workflow locally
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Pytest fixtures
│   ├── test_benchmarks.py  # Unit tests for benchmark functions
│   ├── test_plot.py        # Unit tests for plot generation
│   └── test_integration.py # Integration tests for full workflow
├── results/                # Output directory (created at runtime)
├── requirements.txt        # Runtime dependencies
├── requirements-dev.txt    # Development/test dependencies
├── pytest.ini              # Pytest configuration
└── README.md               # This file
```

## Dependencies

- Python 3.8+
- plotly (Python package for visualization)
- Standard system tools: dd, python3

## Troubleshooting

### Disk benchmark shows 0 MB/s

The disk benchmark requires write access to the temp directory. Ensure sufficient disk space is available.

### Memory benchmark is slow

The memory benchmark allocates 100MB of memory. On systems with limited RAM, this may cause swapping.

### Cannot access results via browser

Ensure the ACTIVATE tunnel session is properly configured and your browser allows popups from the ACTIVATE domain.
