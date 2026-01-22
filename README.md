# Single Node Benchmark Workflow

System benchmarking workflow for the Parallel Works ACTIVATE platform. Runs CPU, memory, and disk I/O benchmarks with support for **SSH**, **SLURM**, and **PBS** schedulers.

## Quick Start

### Deploy to ACTIVATE

1. Push this repository to your ACTIVATE account
2. Select the workflow from your workflows list
3. Choose target cluster (scheduler options auto-populate based on cluster type)
4. Run and view interactive results

### Run Locally

```bash
python scripts/local_runner.py --duration 10 --serve
```

## Supported Schedulers

| Mode | Description |
|------|-------------|
| SSH | Direct execution on cluster head node |
| SLURM | Submit to SLURM scheduler with configurable resources |
| PBS | Submit to PBS scheduler with configurable resources |

Scheduler type is auto-detected from the selected cluster.

## Benchmarks

| Benchmark | Metric | Description |
|-----------|--------|-------------|
| CPU | ops/sec | Prime number calculations |
| Memory | MB/s | Sequential read/write throughput |
| Disk I/O | MB/s | Sequential file read/write |

## Results

- `benchmark_results.json` - Raw results
- `benchmark_results.html` - Interactive Plotly visualization

## Documentation

- [Benchmark Details](docs/benchmarks.md)
- [Scheduler Configuration](docs/scheduler-configuration.md)
- [Development Guide](docs/development.md)

## Project Structure

```
activate-benchmark/
├── workflow.yaml           # ACTIVATE workflow (uses job_runner:v4.0)
├── scripts/                # Benchmark and visualization scripts
├── tests/                  # Pytest test suite
├── docs/                   # Documentation
├── requirements.txt        # Runtime dependencies
└── requirements-dev.txt    # Development dependencies
```
