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


def main() -> int:
    """Main entry point for local runner."""
    parser = argparse.ArgumentParser(
        description="Run single-node benchmarks locally"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=10,
        help="Duration for each benchmark in seconds (default: 10)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./results",
        help="Directory for output files (default: ./results)",
    )
    parser.add_argument(
        "--cpu-only",
        action="store_true",
        help="Run only CPU benchmark",
    )
    parser.add_argument(
        "--memory-only",
        action="store_true",
        help="Run only memory benchmark",
    )
    parser.add_argument(
        "--disk-only",
        action="store_true",
        help="Run only disk I/O benchmark",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start HTTP server after generating results",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for HTTP server (default: 8080)",
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
    from scripts.run_benchmarks import get_system_info, run_all_benchmarks
    from scripts.generate_plot import generate_benchmark_plot

    print("==========================================")
    print("Single Node Benchmark - Local Runner")
    print("==========================================")
    print(f"Duration per test: {args.duration}s")
    print(f"CPU: {run_cpu}, Memory: {run_memory}, Disk: {run_disk}")
    print(f"Output directory: {args.output_dir}")
    print("==========================================")
    print()

    # Collect system info
    system_info = get_system_info()
    print(f"System: {system_info['hostname']}")
    print(f"CPUs: {system_info['cpu_count']}, Memory: {system_info['memory_gb']:.1f} GB")
    print()

    # Run benchmarks
    benchmark_results = run_all_benchmarks(
        duration=args.duration,
        run_cpu=run_cpu,
        run_memory=run_memory,
        run_disk=run_disk,
    )

    # Assemble full results
    results = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "system_info": system_info,
        "benchmarks": benchmark_results,
    }

    # Save JSON results
    results_file = os.path.join(args.output_dir, "benchmark_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print()
    print(f"Results saved to: {results_file}")

    # Generate HTML visualization
    html_file = os.path.join(args.output_dir, "benchmark_results.html")
    generate_benchmark_plot(results, html_file)
    print(f"Visualization saved to: {html_file}")

    # Optionally start server
    if args.serve:
        print()
        print(f"Starting server at http://localhost:{args.port}")
        from scripts.serve_results import start_server
        start_server(args.output_dir, args.port)

    return 0


if __name__ == "__main__":
    sys.exit(main())
