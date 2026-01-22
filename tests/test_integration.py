"""
Integration tests for full workflow execution.
"""

import json
import os
import subprocess

import pytest


class TestLocalRunner:
    """Tests for local runner CLI tool."""

    @pytest.mark.slow
    def test_full_workflow_execution(self, temp_results_dir):
        """Complete workflow runs and produces results."""
        result = subprocess.run(
            [
                "python",
                "scripts/local_runner.py",
                "--duration",
                "3",
                "--output-dir",
                temp_results_dir,
            ],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )
        assert result.returncode == 0, f"Runner failed: {result.stderr}"

        # Check results file exists
        results_file = os.path.join(temp_results_dir, "benchmark_results.json")
        assert os.path.exists(results_file)

        # Validate JSON structure
        with open(results_file) as f:
            data = json.load(f)
        assert "benchmarks" in data
        assert "system_info" in data

    @pytest.mark.slow
    def test_html_output_generated(self, temp_results_dir):
        """HTML visualization is generated."""
        subprocess.run(
            [
                "python",
                "scripts/local_runner.py",
                "--duration",
                "3",
                "--output-dir",
                temp_results_dir,
            ],
            capture_output=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )
        html_file = os.path.join(temp_results_dir, "benchmark_results.html")
        assert os.path.exists(html_file)

    @pytest.mark.slow
    def test_selective_benchmarks_cpu(self, temp_results_dir):
        """Can run only CPU benchmark."""
        result = subprocess.run(
            [
                "python",
                "scripts/local_runner.py",
                "--duration",
                "2",
                "--cpu-only",
                "--output-dir",
                temp_results_dir,
            ],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )
        assert result.returncode == 0, f"Runner failed: {result.stderr}"

        with open(os.path.join(temp_results_dir, "benchmark_results.json")) as f:
            data = json.load(f)
        assert "cpu" in data["benchmarks"]
        assert "memory" not in data["benchmarks"]
        assert "disk" not in data["benchmarks"]

    @pytest.mark.slow
    def test_selective_benchmarks_memory(self, temp_results_dir):
        """Can run only memory benchmark."""
        result = subprocess.run(
            [
                "python",
                "scripts/local_runner.py",
                "--duration",
                "2",
                "--memory-only",
                "--output-dir",
                temp_results_dir,
            ],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )
        assert result.returncode == 0

        with open(os.path.join(temp_results_dir, "benchmark_results.json")) as f:
            data = json.load(f)
        assert "memory" in data["benchmarks"]
        assert "cpu" not in data["benchmarks"]

    def test_results_json_valid_format(self, sample_results_file):
        """Validate results JSON format matches expected schema."""
        with open(sample_results_file) as f:
            data = json.load(f)

        # Check top-level keys
        assert "timestamp" in data
        assert "system_info" in data
        assert "benchmarks" in data

        # Check system_info structure
        sys_info = data["system_info"]
        assert "hostname" in sys_info
        assert "cpu_count" in sys_info
        assert "memory_gb" in sys_info

        # Check benchmarks structure
        benchmarks = data["benchmarks"]
        if "cpu" in benchmarks:
            assert "score" in benchmarks["cpu"]
            assert "duration_sec" in benchmarks["cpu"]
        if "memory" in benchmarks:
            assert "write_mb_s" in benchmarks["memory"]
            assert "read_mb_s" in benchmarks["memory"]
        if "disk" in benchmarks:
            assert "write_mb_s" in benchmarks["disk"]
            assert "read_mb_s" in benchmarks["disk"]


class TestShellScript:
    """Tests for shell script wrapper."""

    @pytest.mark.slow
    def test_shell_script_executes(self, temp_results_dir, monkeypatch):
        """Shell script runs successfully."""
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Set environment variables
        env = os.environ.copy()
        env["DURATION"] = "2"
        env["RUN_CPU"] = "true"
        env["RUN_MEMORY"] = "false"
        env["RUN_DISK"] = "false"
        env["JOB_DIR"] = temp_results_dir

        result = subprocess.run(
            ["bash", "scripts/run_benchmarks.sh"],
            capture_output=True,
            text=True,
            cwd=project_dir,
            env=env,
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"
        assert os.path.exists(os.path.join(temp_results_dir, "benchmark_results.json"))
