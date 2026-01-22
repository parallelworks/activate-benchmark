"""
Pytest fixtures for single-node benchmark tests.
"""

import json
import tempfile

import pytest


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
            "memory_gb": 16.0,
            "platform": "Linux",
            "architecture": "x86_64",
        },
        "benchmarks": {
            "cpu": {
                "score": 5000,
                "primes_found": 1000,
                "numbers_checked": 50000,
                "duration_sec": 10.0,
            },
            "memory": {
                "write_mb_s": 3000.0,
                "read_mb_s": 4500.0,
                "write_iterations": 5,
                "read_iterations": 8,
                "duration_sec": 10.0,
            },
            "disk": {
                "write_mb_s": 400.0,
                "read_mb_s": 600.0,
                "test_size_mb": 256,
                "duration_sec": 10.0,
            },
        },
    }


@pytest.fixture
def sample_results_file(temp_results_dir, sample_benchmark_results):
    """Create a sample results JSON file."""
    import os

    results_file = os.path.join(temp_results_dir, "benchmark_results.json")
    with open(results_file, "w") as f:
        json.dump(sample_benchmark_results, f)
    return results_file


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up environment variables mimicking ACTIVATE runtime."""
    monkeypatch.setenv("DURATION", "5")
    monkeypatch.setenv("RUN_CPU", "true")
    monkeypatch.setenv("RUN_MEMORY", "true")
    monkeypatch.setenv("RUN_DISK", "true")
    monkeypatch.setenv("JOB_DIR", "/tmp/test_job")
