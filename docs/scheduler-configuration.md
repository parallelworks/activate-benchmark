# Scheduler Configuration

## Workflow Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| cluster | compute-clusters | - | Target cluster for benchmark execution |
| duration | number | 10 | Duration for each benchmark in seconds (5-60) |
| run_cpu | boolean | true | Run CPU benchmark |
| run_memory | boolean | true | Run memory benchmark |
| run_disk | boolean | true | Run disk I/O benchmark |

## Scheduler Modes

### SSH Mode

Direct execution on the cluster head node. Best for quick tests or when scheduler overhead is not desired.

- No job queue wait time
- Runs on head node resources
- Suitable for lightweight benchmarks

### SLURM Mode

Submits benchmark as a SLURM job with configurable resources.

- Allocates dedicated compute node
- Respects cluster scheduling policies
- Configurable partition, nodes, and time limits

### PBS Mode

Submits benchmark as a PBS job with configurable resources.

- Allocates dedicated compute node
- Respects cluster scheduling policies
- Configurable queue and resource requests

## Auto-Detection

The scheduler type is automatically detected based on the selected cluster configuration. The workflow will use the appropriate submission method without manual configuration.

## Resource Configuration

For SLURM and PBS modes, the workflow uses sensible defaults:
- Single node allocation
- Standard partition/queue
- Time limit based on benchmark duration + buffer
