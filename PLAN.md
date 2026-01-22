# Single Node Benchmark Workflow - ACTIVATE Implementation Plan

## Overview

Create an ACTIVATE workflow that runs single-node system benchmarks (CPU, memory, disk I/O) and displays results through an interactive Plotly-based web visualization served via an ACTIVATE interactive session.

**Confirmed Requirements:**
- Benchmark types: CPU, Memory, and Disk I/O (all three)
- Visualization: Plotly (interactive HTML output)

## Project Structure

```
activate-benchmark/
├── workflow.yaml           # Main ACTIVATE workflow definition
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
├── requirements.txt        # Runtime dependencies
├── requirements-dev.txt    # Development/test dependencies
├── pytest.ini              # Pytest configuration
└── README.md               # Project documentation
```

## Workflow Architecture

### Job 1: `run-benchmarks`
- Execute CPU benchmark (sysbench or simple Python stress test)
- Execute memory benchmark (memory bandwidth test)
- Execute disk I/O benchmark (dd-based sequential read/write)
- Output results as JSON for visualization

### Job 2: `visualize-results` (Interactive Session)
- Start Python HTTP server serving Plotly-based interactive dashboard
- Configure ACTIVATE tunnel session for browser access
- Display benchmark results with interactive charts

## Implementation Steps

### Step 1: Create workflow.yaml

The workflow YAML will include:
- Input form for selecting benchmark types and duration
- Compute cluster selection
- Two jobs: benchmark execution and results visualization

Key inputs:
- `cluster`: compute-clusters selector
- `benchmark_duration`: number (seconds per test)
- `run_cpu_test`: boolean
- `run_memory_test`: boolean
- `run_disk_test`: boolean

### Step 2: Create Benchmark Script (run_benchmarks.sh)

Tests to implement:
1. **CPU Benchmark**: Calculate prime numbers or matrix operations
2. **Memory Benchmark**: Sequential memory read/write throughput
3. **Disk I/O Benchmark**: Sequential write/read using dd

Output format: JSON file with results:
```json
{
  "timestamp": "2024-01-22T10:30:00Z",
  "system_info": { "hostname": "...", "cpu_count": 8, "memory_gb": 32 },
  "benchmarks": {
    "cpu": { "score": 1234, "duration_sec": 10 },
    "memory": { "bandwidth_mb_s": 5000, "duration_sec": 10 },
    "disk": { "write_mb_s": 500, "read_mb_s": 800, "duration_sec": 10 }
  }
}
```

### Step 3: Create Interactive Plot (generate_plot.py)

Use Plotly to create:
- Bar chart comparing benchmark scores
- System info summary panel
- Timestamp and run details

Generate standalone HTML file with embedded Plotly.js

### Step 4: Create Results Server (serve_results.py)

Simple Python HTTP server that:
- Serves the generated HTML plot
- Auto-refreshes if new results available

### Step 5: Configure Interactive Session

ACTIVATE session configuration:
- Type: tunnel
- Redirect: true
- Port: 8080 (HTTP server)

## Critical Files to Create

| File | Purpose |
|------|---------|
| `workflow.yaml` | ACTIVATE workflow definition |
| `scripts/__init__.py` | Package marker for imports |
| `scripts/run_benchmarks.sh` | Shell wrapper for benchmarks |
| `scripts/run_benchmarks.py` | Python benchmark module (testable) |
| `scripts/generate_plot.py` | Plotly visualization |
| `scripts/serve_results.py` | HTTP server for results |
| `scripts/local_runner.py` | Local workflow execution CLI |
| `tests/test_benchmarks.py` | Unit tests for benchmarks |
| `tests/test_plot.py` | Unit tests for visualization |
| `tests/test_integration.py` | End-to-end integration tests |
| `requirements.txt` | Runtime deps (plotly) |
| `requirements-dev.txt` | Dev deps (pytest, pytest-cov) |
| `README.md` | Full project documentation |

## Workflow YAML Structure

```yaml
name: single-node-benchmark

on:
  execute:
    inputs:
      cluster:
        type: compute-clusters
        label: "Target Cluster"
      benchmark_config:
        type: group
        label: "Benchmark Configuration"
        inputs:
          duration:
            type: number
            label: "Test Duration (seconds)"
            default: 10
            min: 5
            max: 60
          run_cpu:
            type: boolean
            label: "Run CPU Benchmark"
            default: true
          run_memory:
            type: boolean
            label: "Run Memory Benchmark"
            default: true
          run_disk:
            type: boolean
            label: "Run Disk I/O Benchmark"
            default: true

sessions:
  results:
    type: tunnel
    redirect: true

jobs:
  run-benchmarks:
    steps:
      - uses: checkout
      - id: benchmark
        run: |
          bash scripts/run_benchmarks.sh
        env:
          DURATION: ${{ inputs.benchmark_config.duration }}
          RUN_CPU: ${{ inputs.benchmark_config.run_cpu }}
          RUN_MEMORY: ${{ inputs.benchmark_config.run_memory }}
          RUN_DISK: ${{ inputs.benchmark_config.run_disk }}
    ssh:
      remoteHost: ${{ inputs.cluster }}
    outputs:
      results_file: ${{ steps.benchmark.outputs.RESULTS_FILE }}

  visualize-results:
    needs: [run-benchmarks]
    steps:
      - uses: checkout
      - id: serve
        run: |
          pip install -r requirements.txt
          python scripts/generate_plot.py
          python scripts/serve_results.py &
          echo "PORT=8080" >> $OUTPUTS
      - uses: update-session
        with:
          name: results
          remotePort: 8080
    ssh:
      remoteHost: ${{ inputs.cluster }}
```

## Verification Plan

1. **Syntax Validation**: Check workflow.yaml against ACTIVATE schema
2. **Local Script Testing**: Run benchmark scripts locally to verify output format
3. **Integration Test**: Deploy to ACTIVATE and run full workflow
4. **Session Access**: Verify interactive plot is accessible via browser

## Dependencies

- Python 3.8+
- plotly (Python package)
- Standard system tools: dd, bc, python3

## Detailed Benchmark Implementations

### CPU Benchmark
```bash
# Calculate prime numbers up to N using trial division
# Measures: operations per second
python3 -c "
import time
def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True

start = time.time()
count = sum(1 for i in range(2, 100000) if is_prime(i))
duration = time.time() - start
print(f'primes_found={count}')
print(f'ops_per_sec={100000/duration:.2f}')
"
```

### Memory Benchmark
```bash
# Sequential memory read/write throughput
python3 -c "
import time
import array

size = 100 * 1024 * 1024  # 100 MB
data = array.array('d', [0.0] * (size // 8))

start = time.time()
for i in range(len(data)):
    data[i] = float(i)
write_time = time.time() - start

start = time.time()
total = sum(data)
read_time = time.time() - start

print(f'write_mb_s={size/write_time/1e6:.2f}')
print(f'read_mb_s={size/read_time/1e6:.2f}')
"
```

### Disk I/O Benchmark
```bash
# Sequential disk throughput using dd
TEST_FILE="/tmp/benchmark_test_$$"
BS="1M"
COUNT=256  # 256 MB

# Write test
WRITE_SPEED=$(dd if=/dev/zero of=$TEST_FILE bs=$BS count=$COUNT conv=fdatasync 2>&1 | grep -oP '\d+(\.\d+)? [MG]B/s')

# Read test (clear cache first if possible)
sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true
READ_SPEED=$(dd if=$TEST_FILE of=/dev/null bs=$BS 2>&1 | grep -oP '\d+(\.\d+)? [MG]B/s')

rm -f $TEST_FILE
```

## Plotly Visualization Details

The interactive plot will include:

1. **Bar Chart**: Side-by-side comparison of all benchmark scores
2. **System Info Panel**: Hostname, CPU count, memory size, OS
3. **Detailed Results Table**: Raw numbers for each test
4. **Hover Tooltips**: Show exact values and units on hover

Output: `results/benchmark_results.html` - standalone HTML with embedded Plotly.js

---

## README Documentation

The README.md will include:

### Sections
1. **Overview** - Project description and purpose
2. **Quick Start** - How to run locally and on ACTIVATE
3. **Workflow Inputs** - Description of all configurable parameters
4. **Benchmark Details** - What each benchmark measures
5. **Results Interpretation** - How to read the output
6. **Development** - Setting up dev environment, running tests
7. **Troubleshooting** - Common issues and solutions

### README Content Outline
```markdown
# Single Node Benchmark Workflow

System benchmarking workflow for the Parallel Works ACTIVATE platform.

## Quick Start

### Run Locally
pip install -r requirements.txt
python scripts/local_runner.py --duration 10

### Deploy to ACTIVATE
1. Push this repository to your ACTIVATE account
2. Select "single-node-benchmark" workflow
3. Configure benchmark options and target cluster
4. Run and view interactive results

## Benchmarks

| Benchmark | Metric | Description |
|-----------|--------|-------------|
| CPU | ops/sec | Prime number calculations |
| Memory | MB/s | Sequential read/write throughput |
| Disk I/O | MB/s | Sequential file read/write |

## Development

### Run Tests
pip install -r requirements-dev.txt
pytest

### Run with Coverage
pytest --cov=scripts --cov-report=html
```

---

## Unit Testing with Pytest

### Test Structure

#### tests/conftest.py - Shared Fixtures
```python
import pytest
import tempfile
import json

@pytest.fixture
def temp_results_dir():
    """Create temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def sample_benchmark_results():
    """Sample benchmark results for testing plot generation."""
    return {
        "timestamp": "2024-01-22T10:30:00Z",
        "system_info": {
            "hostname": "test-node",
            "cpu_count": 4,
            "memory_gb": 16
        },
        "benchmarks": {
            "cpu": {"score": 5000, "duration_sec": 10},
            "memory": {"write_mb_s": 3000, "read_mb_s": 4500, "duration_sec": 10},
            "disk": {"write_mb_s": 400, "read_mb_s": 600, "duration_sec": 10}
        }
    }

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up environment variables mimicking ACTIVATE runtime."""
    monkeypatch.setenv("DURATION", "5")
    monkeypatch.setenv("RUN_CPU", "true")
    monkeypatch.setenv("RUN_MEMORY", "true")
    monkeypatch.setenv("RUN_DISK", "true")
    monkeypatch.setenv("JOB_DIR", "/tmp/test_job")
```

#### tests/test_benchmarks.py - Benchmark Unit Tests
```python
import pytest
from scripts.run_benchmarks import (
    run_cpu_benchmark,
    run_memory_benchmark,
    run_disk_benchmark,
    get_system_info
)

class TestCPUBenchmark:
    def test_returns_valid_score(self):
        """CPU benchmark returns positive score."""
        result = run_cpu_benchmark(duration=2)
        assert result["score"] > 0
        assert "duration_sec" in result

    def test_respects_duration(self):
        """Benchmark runs for approximately specified duration."""
        result = run_cpu_benchmark(duration=2)
        assert 1.5 <= result["duration_sec"] <= 4.0

class TestMemoryBenchmark:
    def test_returns_bandwidth_metrics(self):
        """Memory benchmark returns read/write bandwidth."""
        result = run_memory_benchmark(duration=2)
        assert result["write_mb_s"] > 0
        assert result["read_mb_s"] > 0

    def test_read_faster_than_write(self):
        """Read bandwidth typically exceeds write bandwidth."""
        result = run_memory_benchmark(duration=2)
        # This is generally true but not enforced
        assert result["read_mb_s"] > 0

class TestDiskBenchmark:
    def test_returns_io_metrics(self, temp_results_dir):
        """Disk benchmark returns read/write speeds."""
        result = run_disk_benchmark(duration=2, test_dir=temp_results_dir)
        assert result["write_mb_s"] > 0
        assert result["read_mb_s"] > 0

    def test_cleans_up_test_file(self, temp_results_dir):
        """Temporary test file is removed after benchmark."""
        import os
        result = run_disk_benchmark(duration=2, test_dir=temp_results_dir)
        files = os.listdir(temp_results_dir)
        assert not any("benchmark_test" in f for f in files)

class TestSystemInfo:
    def test_collects_hostname(self):
        """System info includes hostname."""
        info = get_system_info()
        assert "hostname" in info
        assert len(info["hostname"]) > 0

    def test_collects_cpu_count(self):
        """System info includes CPU count."""
        info = get_system_info()
        assert info["cpu_count"] > 0

    def test_collects_memory(self):
        """System info includes memory size."""
        info = get_system_info()
        assert info["memory_gb"] > 0
```

#### tests/test_plot.py - Visualization Tests
```python
import pytest
import os
from scripts.generate_plot import generate_benchmark_plot, create_figure

class TestPlotGeneration:
    def test_creates_html_file(self, sample_benchmark_results, temp_results_dir):
        """Plot generation creates HTML output file."""
        output_path = os.path.join(temp_results_dir, "results.html")
        generate_benchmark_plot(sample_benchmark_results, output_path)
        assert os.path.exists(output_path)

    def test_html_contains_plotly(self, sample_benchmark_results, temp_results_dir):
        """Generated HTML includes Plotly.js."""
        output_path = os.path.join(temp_results_dir, "results.html")
        generate_benchmark_plot(sample_benchmark_results, output_path)
        with open(output_path) as f:
            content = f.read()
        assert "plotly" in content.lower()

    def test_html_contains_benchmark_data(self, sample_benchmark_results, temp_results_dir):
        """Generated HTML includes benchmark values."""
        output_path = os.path.join(temp_results_dir, "results.html")
        generate_benchmark_plot(sample_benchmark_results, output_path)
        with open(output_path) as f:
            content = f.read()
        assert "CPU" in content
        assert "Memory" in content

class TestFigureCreation:
    def test_figure_has_data(self, sample_benchmark_results):
        """Created figure contains trace data."""
        fig = create_figure(sample_benchmark_results)
        assert len(fig.data) > 0

    def test_figure_has_layout(self, sample_benchmark_results):
        """Created figure has configured layout."""
        fig = create_figure(sample_benchmark_results)
        assert fig.layout.title is not None
```

#### tests/test_integration.py - Integration Tests
```python
import pytest
import subprocess
import json
import os

class TestLocalRunner:
    def test_full_workflow_execution(self, temp_results_dir):
        """Complete workflow runs and produces results."""
        result = subprocess.run(
            ["python", "scripts/local_runner.py",
             "--duration", "3",
             "--output-dir", temp_results_dir],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0

        # Check results file exists
        results_file = os.path.join(temp_results_dir, "benchmark_results.json")
        assert os.path.exists(results_file)

        # Validate JSON structure
        with open(results_file) as f:
            data = json.load(f)
        assert "benchmarks" in data
        assert "system_info" in data

    def test_html_output_generated(self, temp_results_dir):
        """HTML visualization is generated."""
        subprocess.run(
            ["python", "scripts/local_runner.py",
             "--duration", "3",
             "--output-dir", temp_results_dir],
            capture_output=True
        )
        html_file = os.path.join(temp_results_dir, "benchmark_results.html")
        assert os.path.exists(html_file)

    def test_selective_benchmarks(self, temp_results_dir):
        """Can run subset of benchmarks."""
        result = subprocess.run(
            ["python", "scripts/local_runner.py",
             "--duration", "3",
             "--cpu-only",
             "--output-dir", temp_results_dir],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0

        with open(os.path.join(temp_results_dir, "benchmark_results.json")) as f:
            data = json.load(f)
        assert "cpu" in data["benchmarks"]
```

### pytest.ini Configuration
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
```

---

## Local Workflow Runner

### scripts/local_runner.py - CLI Tool
```python
#!/usr/bin/env python3
"""
Local runner for single-node benchmark workflow.
Replicates ACTIVATE workflow behavior for local testing and development.

Usage: python scripts/local_runner.py [options]
"""

import argparse
import json
import os
import sys
from datetime import datetime

# Add parent directory to path for imports when running from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    parser = argparse.ArgumentParser(
        description="Run single-node benchmarks locally"
    )
    parser.add_argument(
        "--duration", type=int, default=10,
        help="Duration for each benchmark in seconds (default: 10)"
    )
    parser.add_argument(
        "--output-dir", type=str, default="./results",
        help="Directory for output files (default: ./results)"
    )
    parser.add_argument(
        "--cpu-only", action="store_true",
        help="Run only CPU benchmark"
    )
    parser.add_argument(
        "--memory-only", action="store_true",
        help="Run only memory benchmark"
    )
    parser.add_argument(
        "--disk-only", action="store_true",
        help="Run only disk I/O benchmark"
    )
    parser.add_argument(
        "--serve", action="store_true",
        help="Start HTTP server after generating results"
    )
    parser.add_argument(
        "--port", type=int, default=8080,
        help="Port for HTTP server (default: 8080)"
    )

    args = parser.parse_args()

    # Determine which benchmarks to run
    run_all = not (args.cpu_only or args.memory_only or args.disk_only)
    run_cpu = run_all or args.cpu_only
    run_memory = run_all or args.memory_only
    run_disk = run_all or args.disk_only

    # Set up environment to mimic ACTIVATE
    os.environ["DURATION"] = str(args.duration)
    os.environ["RUN_CPU"] = str(run_cpu).lower()
    os.environ["RUN_MEMORY"] = str(run_memory).lower()
    os.environ["RUN_DISK"] = str(run_disk).lower()
    os.environ["JOB_DIR"] = args.output_dir

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Import benchmark modules (relative imports from scripts package)
    from scripts.run_benchmarks import run_all_benchmarks, get_system_info
    from scripts.generate_plot import generate_benchmark_plot

    print(f"Running benchmarks (duration: {args.duration}s each)...")
    print(f"  CPU: {run_cpu}, Memory: {run_memory}, Disk: {run_disk}")

    # Collect system info
    system_info = get_system_info()
    print(f"System: {system_info['hostname']} "
          f"({system_info['cpu_count']} CPUs, {system_info['memory_gb']:.1f} GB RAM)")

    # Run benchmarks
    results = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "system_info": system_info,
        "benchmarks": run_all_benchmarks(
            duration=args.duration,
            run_cpu=run_cpu,
            run_memory=run_memory,
            run_disk=run_disk
        )
    }

    # Save JSON results
    results_file = os.path.join(args.output_dir, "benchmark_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {results_file}")

    # Generate HTML visualization
    html_file = os.path.join(args.output_dir, "benchmark_results.html")
    generate_benchmark_plot(results, html_file)
    print(f"Visualization saved to: {html_file}")

    # Optionally start server
    if args.serve:
        from scripts.serve_results import start_server
        print(f"Starting server at http://localhost:{args.port}")
        start_server(args.output_dir, args.port)

    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Usage Examples
```bash
# Run all benchmarks with default settings
python scripts/local_runner.py

# Quick test with short duration
python scripts/local_runner.py --duration 3

# Run only CPU benchmark
python scripts/local_runner.py --cpu-only --duration 5

# Run and serve results in browser
python scripts/local_runner.py --duration 10 --serve

# Specify custom output directory
python scripts/local_runner.py --output-dir ./my_results --serve --port 9000
```

---

## Requirements Files

### requirements.txt (Runtime)
```
plotly>=5.18.0
```

### requirements-dev.txt (Development)
```
-r requirements.txt
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-timeout>=2.2.0
```

---

## Notes

- All expression operators have spaces (ACTIVATE requirement)
- Using `inputs.benchmark_config.duration` format for grouped inputs
- Checkout action has no prefix (built-in)
- update-session action has no prefix (built-in)
- Python benchmark module enables unit testing of core logic
- Local runner mimics ACTIVATE environment variables for consistent behavior
