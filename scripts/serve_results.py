#!/usr/bin/env python3
"""
Simple HTTP server for serving benchmark results.

Serves the generated HTML visualization and supports auto-refresh.
"""

import http.server
import os
import socketserver
from functools import partial


class BenchmarkResultsHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for serving benchmark results."""

    def __init__(self, *args, results_dir: str = "./results", **kwargs):
        self.results_dir = results_dir
        super().__init__(*args, directory=results_dir, **kwargs)

    def do_GET(self) -> None:
        """Handle GET requests with custom routing."""
        # Redirect root to benchmark results
        if self.path == "/" or self.path == "":
            self.path = "/benchmark_results.html"

        # Add cache control headers for HTML to enable refresh
        super().do_GET()

    def end_headers(self) -> None:
        """Add custom headers."""
        # Disable caching for HTML files to allow refresh
        if self.path.endswith(".html"):
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, format: str, *args) -> None:
        """Log requests to stdout."""
        print(f"[HTTP] {args[0]} - {args[1]} {args[2]}")


def start_server(results_dir: str = "./results", port: int = 8080) -> None:
    """
    Start HTTP server for benchmark results.

    Args:
        results_dir: Directory containing results files
        port: Port to serve on
    """
    # Ensure results directory exists
    if not os.path.isdir(results_dir):
        print(f"Error: Results directory not found: {results_dir}")
        return

    # Check for results file
    results_file = os.path.join(results_dir, "benchmark_results.html")
    if not os.path.exists(results_file):
        print(f"Warning: Results file not found: {results_file}")
        print("Server will start but may show 404 until results are generated.")

    # Create handler with custom directory
    handler = partial(BenchmarkResultsHandler, results_dir=results_dir)

    # Allow address reuse
    socketserver.TCPServer.allow_reuse_address = True

    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving benchmark results at http://localhost:{port}")
        print(f"Results directory: {results_dir}")
        print("Press Ctrl+C to stop...")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Serve benchmark results via HTTP"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to serve on (default: 8080)",
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=os.environ.get("JOB_DIR", "./results"),
        help="Results directory (default: ./results or JOB_DIR)",
    )

    args = parser.parse_args()
    start_server(args.dir, args.port)


if __name__ == "__main__":
    main()
