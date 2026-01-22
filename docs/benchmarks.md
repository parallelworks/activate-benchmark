# Benchmark Details

## CPU Benchmark

Calculates prime numbers using trial division. Measures operations per second and tracks the number of primes found during the test duration.

| Metric | Unit | Description |
|--------|------|-------------|
| ops/sec | operations/second | Prime calculation throughput |
| primes_found | count | Total primes discovered |

## Memory Benchmark

Allocates a 100MB buffer and performs sequential write and read operations. Measures throughput in MB/s for both operations.

| Metric | Unit | Description |
|--------|------|-------------|
| write_throughput | MB/s | Sequential write speed |
| read_throughput | MB/s | Sequential read speed |

## Disk I/O Benchmark

Uses `dd` to write a 256MB test file and then read it back. Measures sequential throughput in MB/s. The test file is automatically cleaned up after the benchmark.

| Metric | Unit | Description |
|--------|------|-------------|
| write_throughput | MB/s | Sequential file write speed |
| read_throughput | MB/s | Sequential file read speed |

## Results Format

Results are saved in two formats:

### JSON (`benchmark_results.json`)

Raw benchmark data including:
- Timestamp
- System information
- Individual benchmark metrics
- Duration and configuration

### HTML (`benchmark_results.html`)

Interactive Plotly visualization including:
- Bar charts for each benchmark type
- System information table
- Hover tooltips with detailed metrics

## Troubleshooting

### Disk benchmark shows 0 MB/s

The disk benchmark requires write access to the temp directory. Ensure sufficient disk space is available.

### Memory benchmark is slow

The memory benchmark allocates 100MB of memory. On systems with limited RAM, this may cause swapping.
