"""
Unit tests for benchmark functions.
"""

import pytest

from scripts.run_benchmarks import (
    get_system_info,
    run_all_benchmarks,
    run_cpu_benchmark,
    run_disk_benchmark,
    run_memory_benchmark,
)


class TestCPUBenchmark:
    """Tests for CPU benchmark function."""

    def test_returns_valid_score(self):
        """CPU benchmark returns positive score."""
        result = run_cpu_benchmark(duration=2)
        assert result["score"] > 0
        assert "duration_sec" in result

    def test_respects_duration(self):
        """Benchmark runs for approximately specified duration."""
        result = run_cpu_benchmark(duration=2)
        # Allow some tolerance
        assert 1.5 <= result["duration_sec"] <= 4.0

    def test_returns_primes_found(self):
        """CPU benchmark returns count of primes found."""
        result = run_cpu_benchmark(duration=2)
        assert result["primes_found"] > 0
        assert result["numbers_checked"] > 0

    def test_result_structure(self):
        """CPU benchmark returns expected structure."""
        result = run_cpu_benchmark(duration=2)
        assert "score" in result
        assert "primes_found" in result
        assert "numbers_checked" in result
        assert "duration_sec" in result


class TestMemoryBenchmark:
    """Tests for memory benchmark function."""

    def test_returns_bandwidth_metrics(self):
        """Memory benchmark returns read/write bandwidth."""
        result = run_memory_benchmark(duration=2)
        assert result["write_mb_s"] > 0
        assert result["read_mb_s"] > 0

    def test_returns_iteration_counts(self):
        """Memory benchmark returns iteration counts."""
        result = run_memory_benchmark(duration=2)
        assert result["write_iterations"] >= 1
        assert result["read_iterations"] >= 1

    def test_result_structure(self):
        """Memory benchmark returns expected structure."""
        result = run_memory_benchmark(duration=2)
        assert "write_mb_s" in result
        assert "read_mb_s" in result
        assert "write_iterations" in result
        assert "read_iterations" in result
        assert "duration_sec" in result


class TestDiskBenchmark:
    """Tests for disk I/O benchmark function."""

    def test_returns_io_metrics(self, temp_results_dir):
        """Disk benchmark returns read/write speeds."""
        result = run_disk_benchmark(duration=2, test_dir=temp_results_dir)
        assert result["write_mb_s"] > 0
        assert result["read_mb_s"] > 0

    def test_cleans_up_test_file(self, temp_results_dir):
        """Temporary test file is removed after benchmark."""
        import os

        run_disk_benchmark(duration=2, test_dir=temp_results_dir)
        files = os.listdir(temp_results_dir)
        assert not any("benchmark_test" in f for f in files)

    def test_result_structure(self, temp_results_dir):
        """Disk benchmark returns expected structure."""
        result = run_disk_benchmark(duration=2, test_dir=temp_results_dir)
        assert "write_mb_s" in result
        assert "read_mb_s" in result
        assert "test_size_mb" in result
        assert "duration_sec" in result


class TestSystemInfo:
    """Tests for system info collection."""

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

    def test_collects_platform(self):
        """System info includes platform."""
        info = get_system_info()
        assert "platform" in info
        assert len(info["platform"]) > 0

    def test_collects_architecture(self):
        """System info includes architecture."""
        info = get_system_info()
        assert "architecture" in info
        assert len(info["architecture"]) > 0


class TestRunAllBenchmarks:
    """Tests for combined benchmark runner."""

    def test_runs_all_benchmarks(self, temp_results_dir):
        """Can run all benchmarks together."""
        result = run_all_benchmarks(duration=2, run_cpu=True, run_memory=True, run_disk=True)
        assert "cpu" in result
        assert "memory" in result
        assert "disk" in result

    def test_can_run_cpu_only(self):
        """Can run only CPU benchmark."""
        result = run_all_benchmarks(duration=2, run_cpu=True, run_memory=False, run_disk=False)
        assert "cpu" in result
        assert "memory" not in result
        assert "disk" not in result

    def test_can_run_memory_only(self):
        """Can run only memory benchmark."""
        result = run_all_benchmarks(duration=2, run_cpu=False, run_memory=True, run_disk=False)
        assert "cpu" not in result
        assert "memory" in result
        assert "disk" not in result

    def test_can_run_disk_only(self, temp_results_dir):
        """Can run only disk benchmark."""
        result = run_all_benchmarks(duration=2, run_cpu=False, run_memory=False, run_disk=True)
        assert "cpu" not in result
        assert "memory" not in result
        assert "disk" in result

    def test_empty_when_nothing_selected(self):
        """Returns empty dict when no benchmarks selected."""
        result = run_all_benchmarks(duration=2, run_cpu=False, run_memory=False, run_disk=False)
        assert result == {}
