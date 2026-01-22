"""
Unit tests for plot generation.
"""

import os

import pytest

from scripts.generate_plot import create_figure, generate_benchmark_plot


class TestPlotGeneration:
    """Tests for HTML plot generation."""

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

    def test_html_contains_system_info(self, sample_benchmark_results, temp_results_dir):
        """Generated HTML includes system information."""
        output_path = os.path.join(temp_results_dir, "results.html")
        generate_benchmark_plot(sample_benchmark_results, output_path)
        with open(output_path) as f:
            content = f.read()
        assert "test-node" in content  # hostname

    def test_html_is_valid(self, sample_benchmark_results, temp_results_dir):
        """Generated HTML has valid structure."""
        output_path = os.path.join(temp_results_dir, "results.html")
        generate_benchmark_plot(sample_benchmark_results, output_path)
        with open(output_path) as f:
            content = f.read()
        assert content.startswith("<")
        assert "</html>" in content


class TestFigureCreation:
    """Tests for Plotly figure creation."""

    def test_figure_has_data(self, sample_benchmark_results):
        """Created figure contains trace data."""
        fig = create_figure(sample_benchmark_results)
        assert len(fig.data) > 0

    def test_figure_has_layout(self, sample_benchmark_results):
        """Created figure has configured layout."""
        fig = create_figure(sample_benchmark_results)
        assert fig.layout.title is not None

    def test_figure_includes_cpu_trace(self, sample_benchmark_results):
        """Figure includes CPU benchmark data."""
        fig = create_figure(sample_benchmark_results)
        # Check that we have bar traces (CPU, memory, disk)
        bar_traces = [t for t in fig.data if t.type == "bar"]
        assert len(bar_traces) >= 1

    def test_figure_includes_table(self, sample_benchmark_results):
        """Figure includes system info table."""
        fig = create_figure(sample_benchmark_results)
        table_traces = [t for t in fig.data if t.type == "table"]
        assert len(table_traces) == 1

    def test_handles_missing_benchmarks(self):
        """Figure handles missing benchmark types gracefully."""
        partial_results = {
            "timestamp": "2024-01-22T10:30:00Z",
            "system_info": {"hostname": "test", "cpu_count": 4, "memory_gb": 16.0},
            "benchmarks": {
                "cpu": {"score": 5000, "duration_sec": 10.0},
            },
        }
        fig = create_figure(partial_results)
        assert len(fig.data) > 0

    def test_handles_empty_benchmarks(self):
        """Figure handles empty benchmarks dictionary."""
        empty_results = {
            "timestamp": "2024-01-22T10:30:00Z",
            "system_info": {"hostname": "test", "cpu_count": 4, "memory_gb": 16.0},
            "benchmarks": {},
        }
        fig = create_figure(empty_results)
        # Should still have the table
        assert len(fig.data) >= 1
