"""
Performance Benchmarks

Tests specific API endpoints and measures performance metrics.
"""

import time
import statistics
import requests
import json
from typing import List, Dict, Any
from datetime import datetime


class PerformanceBenchmark:
    """Performance testing and benchmarking utilities"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []

    def measure_endpoint(
        self,
        method: str,
        endpoint: str,
        iterations: int = 100,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Measure endpoint performance

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            iterations: Number of iterations
            **kwargs: Additional request parameters

        Returns:
            Performance metrics dictionary
        """
        response_times = []
        status_codes = []
        errors = []

        url = f"{self.base_url}{endpoint}"

        print(f"\nTesting {method} {endpoint} ({iterations} iterations)...")

        for i in range(iterations):
            try:
                start_time = time.time()

                if method == "GET":
                    response = requests.get(url, timeout=10, **kwargs)
                elif method == "POST":
                    response = requests.post(url, timeout=10, **kwargs)
                elif method == "PUT":
                    response = requests.put(url, timeout=10, **kwargs)
                elif method == "DELETE":
                    response = requests.delete(url, timeout=10, **kwargs)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                elapsed = (time.time() - start_time) * 1000  # Convert to ms

                response_times.append(elapsed)
                status_codes.append(response.status_code)

            except Exception as e:
                errors.append(str(e))

        # Calculate statistics
        if response_times:
            metrics = {
                "endpoint": f"{method} {endpoint}",
                "iterations": iterations,
                "success_rate": (len(response_times) / iterations) * 100,
                "min_time": round(min(response_times), 2),
                "max_time": round(max(response_times), 2),
                "avg_time": round(statistics.mean(response_times), 2),
                "median_time": round(statistics.median(response_times), 2),
                "p95_time": round(statistics.quantiles(response_times, n=20)[18], 2),
                "p99_time": round(statistics.quantiles(response_times, n=100)[98], 2),
                "errors": len(errors),
                "error_rate": (len(errors) / iterations) * 100,
                "timestamp": datetime.now().isoformat(),
            }

            self.results.append(metrics)
            self._print_metrics(metrics)
            return metrics
        else:
            print(f"ERROR: All requests failed")
            return {"error": "All requests failed", "errors": errors}

    def _print_metrics(self, metrics: Dict[str, Any]):
        """Print metrics in readable format"""
        print(f"  Success Rate: {metrics['success_rate']:.1f}%")
        print(f"  Min: {metrics['min_time']}ms")
        print(f"  Avg: {metrics['avg_time']}ms")
        print(f"  Median: {metrics['median_time']}ms")
        print(f"  P95: {metrics['p95_time']}ms")
        print(f"  P99: {metrics['p99_time']}ms")
        print(f"  Max: {metrics['max_time']}ms")
        if metrics['errors'] > 0:
            print(f"  Errors: {metrics['errors']} ({metrics['error_rate']:.1f}%)")

    def run_all_benchmarks(self):
        """Run comprehensive benchmark suite"""
        print("="*80)
        print("CivicQ Performance Benchmark Suite")
        print("="*80)

        # Health check
        self.measure_endpoint("GET", "/health", iterations=50)

        # Ballot endpoints
        self.measure_endpoint("GET", "/api/ballots/los-angeles", iterations=100)
        self.measure_endpoint("GET", "/api/ballots/1", iterations=100)

        # Contest endpoints
        self.measure_endpoint("GET", "/api/contests/1", iterations=100)
        self.measure_endpoint("GET", "/api/contests/1/candidates", iterations=100)

        # Question endpoints
        self.measure_endpoint("GET", "/api/questions?page=1&limit=20", iterations=100)
        self.measure_endpoint("GET", "/api/questions/1", iterations=100)
        self.measure_endpoint("GET", "/api/questions/trending?limit=20", iterations=100)

        # Candidate endpoints
        self.measure_endpoint("GET", "/api/candidates/1", iterations=100)

        # City endpoints
        self.measure_endpoint("GET", "/api/cities", iterations=100)
        self.measure_endpoint("GET", "/api/cities/los-angeles", iterations=100)

        # Video endpoints
        self.measure_endpoint("GET", "/api/videos/1", iterations=50)

        print("\n" + "="*80)
        print("Benchmark Suite Completed")
        print("="*80)

        self.print_summary()

    def print_summary(self):
        """Print summary of all benchmarks"""
        if not self.results:
            print("No results to summarize")
            return

        print("\nPERFORMANCE SUMMARY")
        print("-"*80)
        print(f"{'Endpoint':<50} {'Avg (ms)':<12} {'P95 (ms)':<12} {'Success %':<12}")
        print("-"*80)

        for result in self.results:
            endpoint = result['endpoint'][:48]
            avg = result['avg_time']
            p95 = result['p95_time']
            success = result['success_rate']
            print(f"{endpoint:<50} {avg:<12} {p95:<12} {success:<12.1f}")

        print("-"*80)

        # Overall statistics
        all_avgs = [r['avg_time'] for r in self.results]
        all_p95s = [r['p95_time'] for r in self.results]
        all_success = [r['success_rate'] for r in self.results]

        print(f"{'OVERALL':<50} {statistics.mean(all_avgs):<12.2f} {statistics.mean(all_p95s):<12.2f} {statistics.mean(all_success):<12.1f}")
        print("="*80)

    def save_results(self, filename: str = "benchmark_results.json"):
        """Save results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to {filename}")

    def check_performance_targets(self) -> bool:
        """
        Check if performance meets targets

        Targets:
        - API endpoints: avg < 200ms, p95 < 500ms
        - Database queries: avg < 100ms
        - Video streaming: avg < 300ms
        - Success rate: > 99%

        Returns:
            True if all targets met
        """
        print("\nCHECKING PERFORMANCE TARGETS")
        print("-"*80)

        all_passed = True

        for result in self.results:
            endpoint = result['endpoint']
            passed = True
            issues = []

            # Check average response time
            if result['avg_time'] > 200:
                passed = False
                issues.append(f"Avg ({result['avg_time']}ms) > 200ms")

            # Check P95 response time
            if result['p95_time'] > 500:
                passed = False
                issues.append(f"P95 ({result['p95_time']}ms) > 500ms")

            # Check success rate
            if result['success_rate'] < 99:
                passed = False
                issues.append(f"Success rate ({result['success_rate']}%) < 99%")

            status = "PASS" if passed else "FAIL"
            print(f"{status}: {endpoint}")
            if issues:
                for issue in issues:
                    print(f"  - {issue}")

            if not passed:
                all_passed = False

        print("-"*80)
        if all_passed:
            print("All performance targets met!")
        else:
            print("Some performance targets not met. Review failures above.")
        print("="*80)

        return all_passed


def main():
    """Run benchmark suite"""
    import argparse

    parser = argparse.ArgumentParser(description="CivicQ Performance Benchmarks")
    parser.add_argument(
        "--host",
        default="http://localhost:8000",
        help="API host URL"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Number of iterations per test"
    )
    parser.add_argument(
        "--output",
        default="benchmark_results.json",
        help="Output file for results"
    )

    args = parser.parse_args()

    # Run benchmarks
    benchmark = PerformanceBenchmark(base_url=args.host)
    benchmark.run_all_benchmarks()
    benchmark.save_results(args.output)
    benchmark.check_performance_targets()


if __name__ == "__main__":
    main()
