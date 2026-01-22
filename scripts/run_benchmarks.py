#!/usr/bin/env python3
"""
Python benchmark module for single-node system benchmarks.

Provides testable implementations of CPU, memory, and disk I/O benchmarks.
"""

import os
import platform
import socket
import subprocess
import tempfile
import time
from typing import Any


def get_system_info() -> dict[str, Any]:
    """Collect system information for benchmark context."""
    cpu_count = os.cpu_count() or 1

    # Get memory size
    memory_gb = 0.0
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    # MemTotal is in kB
                    mem_kb = int(line.split()[1])
                    memory_gb = mem_kb / (1024 * 1024)
                    break
    except (OSError, ValueError):
        # Fallback for non-Linux systems
        try:
            import shutil
            total, _, _ = shutil.disk_usage("/")
            # This is disk, not memory - use a different approach
            memory_gb = 8.0  # Default fallback
        except Exception:
            memory_gb = 8.0

    return {
        "hostname": socket.gethostname(),
        "cpu_count": cpu_count,
        "memory_gb": round(memory_gb, 2),
        "platform": platform.system(),
        "architecture": platform.machine(),
    }


def run_cpu_benchmark(duration: int = 10) -> dict[str, Any]:
    """
    Run CPU benchmark using prime number calculations.

    Args:
        duration: Target duration in seconds

    Returns:
        Dictionary with score and actual duration
    """
    def is_prime(n: int) -> bool:
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(n ** 0.5) + 1, 2):
            if n % i == 0:
                return False
        return True

    start_time = time.time()
    end_time = start_time + duration

    primes_found = 0
    current_number = 2

    while time.time() < end_time:
        # Check a batch of numbers
        batch_size = 1000
        for _ in range(batch_size):
            if is_prime(current_number):
                primes_found += 1
            current_number += 1

    actual_duration = time.time() - start_time
    operations_per_second = current_number / actual_duration

    return {
        "score": int(operations_per_second),
        "primes_found": primes_found,
        "numbers_checked": current_number - 2,
        "duration_sec": round(actual_duration, 2),
    }


def run_memory_benchmark(duration: int = 10) -> dict[str, Any]:
    """
    Run memory benchmark measuring sequential read/write throughput.

    Args:
        duration: Target duration in seconds

    Returns:
        Dictionary with read/write bandwidth in MB/s
    """
    import array

    # Use 100MB buffer for testing
    buffer_size = 100 * 1024 * 1024  # 100 MB
    num_elements = buffer_size // 8  # 8 bytes per double

    # Allocate buffer
    data = array.array('d', [0.0] * num_elements)

    # Write benchmark
    write_start = time.time()
    write_end = write_start + (duration / 2)
    write_iterations = 0

    while time.time() < write_end:
        for i in range(num_elements):
            data[i] = float(i)
        write_iterations += 1

    write_duration = time.time() - write_start
    write_bytes = write_iterations * buffer_size
    write_mb_s = (write_bytes / write_duration) / (1024 * 1024)

    # Read benchmark
    read_start = time.time()
    read_end = read_start + (duration / 2)
    read_iterations = 0

    while time.time() < read_end:
        total = sum(data)  # noqa: F841
        read_iterations += 1

    read_duration = time.time() - read_start
    read_bytes = read_iterations * buffer_size
    read_mb_s = (read_bytes / read_duration) / (1024 * 1024)

    actual_duration = write_duration + read_duration

    return {
        "write_mb_s": round(write_mb_s, 2),
        "read_mb_s": round(read_mb_s, 2),
        "write_iterations": write_iterations,
        "read_iterations": read_iterations,
        "duration_sec": round(actual_duration, 2),
    }


def run_disk_benchmark(duration: int = 10, test_dir: str | None = None) -> dict[str, Any]:
    """
    Run disk I/O benchmark measuring sequential read/write throughput.

    Args:
        duration: Target duration in seconds
        test_dir: Directory for test file (default: system temp)

    Returns:
        Dictionary with read/write speeds in MB/s
    """
    if test_dir is None:
        test_dir = tempfile.gettempdir()

    test_file = os.path.join(test_dir, f"benchmark_test_{os.getpid()}")
    block_size = 1024 * 1024  # 1 MB blocks
    test_size_mb = 256  # 256 MB test file

    write_mb_s = 0.0
    read_mb_s = 0.0

    try:
        # Write benchmark using dd
        write_cmd = [
            "dd",
            "if=/dev/zero",
            f"of={test_file}",
            f"bs={block_size}",
            f"count={test_size_mb}",
            "conv=fdatasync",
        ]

        write_start = time.time()
        result = subprocess.run(
            write_cmd,
            capture_output=True,
            text=True,
        )
        write_duration = time.time() - write_start

        if result.returncode == 0:
            write_mb_s = test_size_mb / write_duration

        # Try to clear cache (may require root)
        try:
            subprocess.run(
                ["sync"],
                capture_output=True,
            )
            # Attempt to drop caches (will silently fail without root)
            subprocess.run(
                ["sh", "-c", "echo 3 > /proc/sys/vm/drop_caches"],
                capture_output=True,
            )
        except Exception:
            pass

        # Read benchmark using dd
        read_cmd = [
            "dd",
            f"if={test_file}",
            "of=/dev/null",
            f"bs={block_size}",
        ]

        read_start = time.time()
        result = subprocess.run(
            read_cmd,
            capture_output=True,
            text=True,
        )
        read_duration = time.time() - read_start

        if result.returncode == 0:
            read_mb_s = test_size_mb / read_duration

    finally:
        # Clean up test file
        try:
            os.remove(test_file)
        except OSError:
            pass

    return {
        "write_mb_s": round(write_mb_s, 2),
        "read_mb_s": round(read_mb_s, 2),
        "test_size_mb": test_size_mb,
        "duration_sec": round(duration, 2),
    }


def run_all_benchmarks(
    duration: int = 10,
    run_cpu: bool = True,
    run_memory: bool = True,
    run_disk: bool = True,
) -> dict[str, Any]:
    """
    Run all selected benchmarks.

    Args:
        duration: Duration for each benchmark in seconds
        run_cpu: Whether to run CPU benchmark
        run_memory: Whether to run memory benchmark
        run_disk: Whether to run disk I/O benchmark

    Returns:
        Dictionary with results from all benchmarks
    """
    results = {}

    if run_cpu:
        print("Running CPU benchmark...")
        results["cpu"] = run_cpu_benchmark(duration)
        print(f"  Score: {results['cpu']['score']} ops/sec")

    if run_memory:
        print("Running memory benchmark...")
        results["memory"] = run_memory_benchmark(duration)
        print(f"  Write: {results['memory']['write_mb_s']} MB/s, "
              f"Read: {results['memory']['read_mb_s']} MB/s")

    if run_disk:
        print("Running disk I/O benchmark...")
        results["disk"] = run_disk_benchmark(duration)
        print(f"  Write: {results['disk']['write_mb_s']} MB/s, "
              f"Read: {results['disk']['read_mb_s']} MB/s")

    return results


if __name__ == "__main__":
    import json

    # Run with default settings when executed directly
    system_info = get_system_info()
    print(f"System: {system_info['hostname']}")
    print(f"CPUs: {system_info['cpu_count']}, Memory: {system_info['memory_gb']} GB")
    print()

    results = run_all_benchmarks(duration=5)
    print()
    print("Results:")
    print(json.dumps(results, indent=2))
