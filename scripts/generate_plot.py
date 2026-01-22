#!/usr/bin/env python3
"""
Generate interactive Plotly visualization for benchmark results.
"""

import json
import os
from typing import Any

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_figure(results: dict[str, Any]) -> go.Figure:
    """
    Create Plotly figure from benchmark results.

    Args:
        results: Benchmark results dictionary

    Returns:
        Plotly Figure object
    """
    benchmarks = results.get("benchmarks", {})
    system_info = results.get("system_info", {})
    timestamp = results.get("timestamp", "Unknown")

    # Create subplot with 2 rows
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "CPU Benchmark",
            "Memory Bandwidth",
            "Disk I/O Throughput",
            "System Information",
        ),
        specs=[
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "table"}],
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.1,
    )

    # CPU Benchmark
    if "cpu" in benchmarks:
        cpu_data = benchmarks["cpu"]
        primes = cpu_data.get("primes_found")
        primes_str = f"{primes:,}" if isinstance(primes, int) else "N/A"
        fig.add_trace(
            go.Bar(
                x=["Operations/sec"],
                y=[cpu_data.get("score", 0)],
                name="CPU Score",
                marker_color="#636EFA",
                text=[f"{cpu_data.get('score', 0):,}"],
                textposition="outside",
                hovertemplate=(
                    "CPU Benchmark<br>"
                    "Score: %{y:,.0f} ops/sec<br>"
                    f"Primes found: {primes_str}<br>"
                    f"Duration: {cpu_data.get('duration_sec', 'N/A')}s"
                    "<extra></extra>"
                ),
            ),
            row=1,
            col=1,
        )

    # Memory Bandwidth
    if "memory" in benchmarks:
        mem_data = benchmarks["memory"]
        fig.add_trace(
            go.Bar(
                x=["Write", "Read"],
                y=[mem_data.get("write_mb_s", 0), mem_data.get("read_mb_s", 0)],
                name="Memory",
                marker_color=["#EF553B", "#00CC96"],
                text=[
                    f"{mem_data.get('write_mb_s', 0):.0f}",
                    f"{mem_data.get('read_mb_s', 0):.0f}",
                ],
                textposition="outside",
                hovertemplate=(
                    "Memory Bandwidth<br>"
                    "%{x}: %{y:,.0f} MB/s<br>"
                    f"Duration: {mem_data.get('duration_sec', 'N/A')}s"
                    "<extra></extra>"
                ),
            ),
            row=1,
            col=2,
        )

    # Disk I/O
    if "disk" in benchmarks:
        disk_data = benchmarks["disk"]
        fig.add_trace(
            go.Bar(
                x=["Write", "Read"],
                y=[disk_data.get("write_mb_s", 0), disk_data.get("read_mb_s", 0)],
                name="Disk I/O",
                marker_color=["#AB63FA", "#FFA15A"],
                text=[
                    f"{disk_data.get('write_mb_s', 0):.0f}",
                    f"{disk_data.get('read_mb_s', 0):.0f}",
                ],
                textposition="outside",
                hovertemplate=(
                    "Disk I/O<br>"
                    "%{x}: %{y:,.0f} MB/s<br>"
                    f"Test size: {disk_data.get('test_size_mb', 'N/A')} MB"
                    "<extra></extra>"
                ),
            ),
            row=2,
            col=1,
        )

    # System Info Table
    sys_headers = ["Property", "Value"]
    sys_cells = [
        [
            "Hostname",
            "CPU Count",
            "Memory",
            "Platform",
            "Architecture",
            "Timestamp",
        ],
        [
            system_info.get("hostname", "N/A"),
            str(system_info.get("cpu_count", "N/A")),
            f"{system_info.get('memory_gb', 0):.1f} GB",
            system_info.get("platform", "N/A"),
            system_info.get("architecture", "N/A"),
            timestamp[:19].replace("T", " ") if timestamp else "N/A",
        ],
    ]

    fig.add_trace(
        go.Table(
            header=dict(
                values=sys_headers,
                fill_color="#636EFA",
                font=dict(color="white", size=12),
                align="left",
            ),
            cells=dict(
                values=sys_cells,
                fill_color="white",
                font=dict(size=11),
                align="left",
                height=25,
            ),
        ),
        row=2,
        col=2,
    )

    # Update layout
    hostname = system_info.get("hostname", "Unknown")
    fig.update_layout(
        title=dict(
            text=f"System Benchmark Results - {hostname}",
            font=dict(size=20),
        ),
        showlegend=False,
        height=700,
        template="plotly_white",
    )

    # Update y-axis labels
    fig.update_yaxes(title_text="Operations/sec", row=1, col=1)
    fig.update_yaxes(title_text="MB/s", row=1, col=2)
    fig.update_yaxes(title_text="MB/s", row=2, col=1)

    return fig


def generate_benchmark_plot(
    results: dict[str, Any],
    output_path: str,
) -> None:
    """
    Generate HTML benchmark visualization.

    Args:
        results: Benchmark results dictionary
        output_path: Path for output HTML file
    """
    fig = create_figure(results)

    # Write standalone HTML
    fig.write_html(
        output_path,
        include_plotlyjs=True,
        full_html=True,
        config={
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        },
    )


def main() -> None:
    """Main entry point for plot generation."""
    # Default paths
    job_dir = os.environ.get("JOB_DIR", "./results")
    results_file = os.path.join(job_dir, "benchmark_results.json")
    output_file = os.path.join(job_dir, "benchmark_results.html")

    # Check if results file exists
    if not os.path.exists(results_file):
        print(f"Error: Results file not found: {results_file}")
        return

    # Load results
    with open(results_file) as f:
        results = json.load(f)

    # Generate plot
    generate_benchmark_plot(results, output_file)
    print(f"Visualization generated: {output_file}")


if __name__ == "__main__":
    main()
