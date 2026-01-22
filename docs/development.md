# Development Guide

## Setup

```bash
# Activate shared virtual environment and install development dependencies
source ~/venv/bin/activate
uv pip install -r requirements-dev.txt
```

## Dependencies

- Python 3.8+
- uv (fast Python package installer)
- plotly (Python package for visualization)
- Standard system tools: dd, python3
- Shared virtual environment at `~/venv`

## Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scripts --cov-report=html

# Skip slow integration tests
pytest -m "not slow"
```

## Local Runner

The local runner allows testing the benchmark workflow without deploying to ACTIVATE.

### Options

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
└── README.md
```

## Troubleshooting

### Cannot access results via browser

Ensure the ACTIVATE tunnel session is properly configured and your browser allows popups from the ACTIVATE domain.
