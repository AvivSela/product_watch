#!/usr/bin/env python3
"""
Script to run all service tests from project root.
Supports both unit tests and integration tests.
"""

import argparse
import os
import subprocess
import sys


def run_service_tests(service_name, service_dir, test_type="unit"):
    """Run tests for a specific service."""
    test_dir = os.path.join(service_dir, "tests")

    if test_type == "integration":
        test_dir = os.path.join(test_dir, "integration")
        print(f"\n🧪 Running {service_name} integration tests...")
        # Run integration tests (including performance tests)
        pytest_args = [
            sys.executable,
            "-m",
            "pytest",
            test_dir,
            "-v",
            "--tb=short",
            "-m",
            "integration",
        ]
    else:
        print(f"\n🧪 Running {service_name} unit tests...")
        # Run only unit tests (exclude integration and performance tests)
        pytest_args = [
            sys.executable,
            "-m",
            "pytest",
            test_dir,
            "-v",
            "--tb=short",
            "-m",
            "unit",
        ]

    try:
        result = subprocess.run(
            pytest_args,
            cwd=service_dir,
            check=True,
        )
        print(f"✅ All {service_name} {test_type} tests passed!")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(
            f"❌ {service_name} {test_type} tests failed with exit code {e.returncode}"
        )
        return e.returncode


def run_integration_tests():
    """Run integration tests using Docker Compose."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    integration_script = os.path.join(
        project_root, "scripts", "run_integration_tests.py"
    )

    print("\n🧪 Running integration tests with Docker Compose...")
    try:
        result = subprocess.run([sys.executable, integration_script], check=True)
        print("✅ All integration tests passed!")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ Integration tests failed with exit code {e.returncode}")
        return e.returncode


def run_all_tests(test_type="unit"):
    """Run all service tests from project root."""
    project_root = os.path.dirname(os.path.abspath(__file__))

    # Define services
    services = [
        (
            "Product Service",
            os.path.join(project_root, "src", "services", "product_service"),
        ),
        (
            "Store Service",
            os.path.join(project_root, "src", "services", "store_service"),
        ),
        (
            "Price Service",
            os.path.join(project_root, "src", "services", "price_service"),
        ),
        (
            "Retail File Service",
            os.path.join(project_root, "src", "services", "retail_file_service"),
        ),
    ]

    total_exit_code = 0

    for service_name, service_dir in services:
        exit_code = run_service_tests(service_name, service_dir, test_type)
        if exit_code != 0:
            total_exit_code = exit_code

    if total_exit_code == 0:
        print(f"\n🎉 All service {test_type} tests passed!")
    else:
        print(f"\n💥 Some {test_type} tests failed with exit code {total_exit_code}")

    return total_exit_code


def run_all_test_types():
    """Run all test types (unit + integration)."""
    print("🚀 Running all test types...")

    # Run unit tests first
    print("\n" + "=" * 50)
    print("UNIT TESTS")
    print("=" * 50)
    unit_exit_code = run_all_tests("unit")

    # Run integration tests
    print("\n" + "=" * 50)
    print("INTEGRATION TESTS")
    print("=" * 50)
    integration_exit_code = run_integration_tests()

    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)

    if unit_exit_code == 0:
        print("✅ Unit tests: PASSED")
    else:
        print(f"❌ Unit tests: FAILED (exit code {unit_exit_code})")

    if integration_exit_code == 0:
        print("✅ Integration tests: PASSED")
    else:
        print(f"❌ Integration tests: FAILED (exit code {integration_exit_code})")

    total_exit_code = unit_exit_code or integration_exit_code

    if total_exit_code == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n💥 Some tests failed with exit code {total_exit_code}")

    return total_exit_code


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(description="Run service tests")
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "all"],
        default="unit",
        help="Type of tests to run (default: unit)",
    )

    args = parser.parse_args()

    if args.type == "all":
        exit_code = run_all_test_types()
    elif args.type == "integration":
        exit_code = run_integration_tests()
    else:  # unit tests
        exit_code = run_all_tests("unit")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
