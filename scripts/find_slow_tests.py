#!/usr/bin/env python3
"""
Script to find tests that take more than a specified duration.
Usage: python scripts/find_slow_tests.py [threshold_seconds] [service_name]
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


def run_tests_with_timing(service_dir, test_type="unit", threshold=2.0):
    """Run tests and report those taking longer than threshold."""
    test_dir = os.path.join(service_dir, "tests")

    if test_type == "integration":
        test_dir = os.path.join(test_dir, "integration")
        pytest_args = [
            sys.executable,
            "-m",
            "pytest",
            test_dir,
            "-v",
            "--tb=short",
            "-m",
            "integration",
            "--durations=0",  # Show all durations
        ]
    else:
        pytest_args = [
            sys.executable,
            "-m",
            "pytest",
            test_dir,
            "-v",
            "--tb=short",
            "-m",
            "unit",
            "--durations=0",  # Show all durations
        ]

    print(f"Running tests in {service_dir}...")
    start_time = time.time()

    try:
        result = subprocess.run(
            pytest_args, cwd=service_dir, capture_output=True, text=True, check=True
        )

        total_time = time.time() - start_time
        print(f"Total test time: {total_time:.2f} seconds")

        # Parse output for slow tests
        slow_tests = []
        lines = result.stdout.split("\n")

        # Look for duration information in pytest output
        for line in lines:
            if "slowest" in line.lower() or "duration" in line.lower():
                print(f"DURATION INFO: {line}")

        # Also check stderr for duration info
        for line in result.stderr.split("\n"):
            if "slowest" in line.lower() or "duration" in line.lower():
                print(f"DURATION INFO: {line}")

        return result.returncode

    except subprocess.CalledProcessError as e:
        print(f"Tests failed with exit code {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return e.returncode


def find_slow_tests(threshold=2.0, service=None, test_type="unit"):
    """Find slow tests across all services or a specific service."""
    project_root = Path(__file__).parent.parent

    services = [
        ("Product Service", "src/services/product_service"),
        ("Store Service", "src/services/store_service"),
        ("Price Service", "src/services/price_service"),
        ("Retail File Service", "src/services/retail_file_service"),
    ]

    if service:
        # Filter to specific service
        services = [
            (name, path) for name, path in services if service.lower() in name.lower()
        ]

    print(f"🔍 Finding tests taking more than {threshold} seconds...")
    print(f"Test type: {test_type}")
    print("=" * 60)

    total_exit_code = 0

    for service_name, service_path in services:
        full_path = project_root / service_path
        if not full_path.exists():
            print(f"⚠️ Service directory not found: {full_path}")
            continue

        print(f"\n📦 {service_name}")
        print("-" * 40)

        exit_code = run_tests_with_timing(str(full_path), test_type, threshold)
        if exit_code != 0:
            total_exit_code = exit_code

    return total_exit_code


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(description="Find slow tests")
    parser.add_argument(
        "--threshold",
        type=float,
        default=2.0,
        help="Minimum duration in seconds to report (default: 2.0)",
    )
    parser.add_argument(
        "--service",
        choices=["product", "store", "price", "retail"],
        help="Specific service to test (default: all services)",
    )
    parser.add_argument(
        "--type",
        choices=["unit", "integration"],
        default="unit",
        help="Type of tests to run (default: unit)",
    )

    args = parser.parse_args()

    exit_code = find_slow_tests(args.threshold, args.service, args.type)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
