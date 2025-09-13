#!/usr/bin/env python3
"""
Script to run both unit and integration tests with combined coverage reporting.

This script:
1. Runs unit tests for all services with coverage
2. Runs integration tests for all services with coverage
3. Combines the coverage data from both test types
4. Generates comprehensive coverage reports

Usage:
  python scripts/run_coverage_tests.py                    # Run all tests with coverage
  python scripts/run_coverage_tests.py --unit-only        # Run only unit tests with coverage
  python scripts/run_coverage_tests.py --integration-only # Run only integration tests with coverage
  python scripts/run_coverage_tests.py --service retail   # Run tests for specific service only
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def run_command(command, cwd=None, check=True, capture_output=True, env=None):
    """Run a command and return the result."""
    print(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=check,
            capture_output=capture_output,
            text=True,
            env=env,
        )
        if not capture_output and result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        raise


def cleanup_coverage_files(project_root):
    """Clean up existing coverage files."""
    print("🧹 Cleaning up existing coverage files...")

    coverage_files = [".coverage", "coverage.xml", "htmlcov", "coverage.json"]

    for service_dir in get_service_dirs(project_root):
        for file in coverage_files:
            file_path = os.path.join(service_dir, file)
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    import shutil

                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
                print(f"  Removed: {file_path}")


def get_service_dirs(project_root):
    """Get list of service directories."""
    services_dir = os.path.join(project_root, "src", "services")
    return [
        os.path.join(services_dir, "product_service"),
        os.path.join(services_dir, "store_service"),
        os.path.join(services_dir, "price_service"),
        os.path.join(services_dir, "retail_file_service"),
    ]


def run_unit_tests_with_coverage(project_root, service_name=None):
    """Run unit tests with coverage for all services or specific service."""
    print("\n" + "=" * 60)
    print("RUNNING UNIT TESTS WITH COVERAGE")
    print("=" * 60)

    service_dirs = get_service_dirs(project_root)
    if service_name:
        service_dirs = [d for d in service_dirs if service_name in d]

    total_exit_code = 0

    for service_dir in service_dirs:
        service_name = os.path.basename(service_dir)
        print(f"\n🧪 Running {service_name} unit tests with coverage...")

        # Run unit tests with coverage
        pytest_args = [
            sys.executable,
            "-m",
            "pytest",
            "tests",
            "-v",
            "--tb=short",
            "-m",
            "unit",
            "--cov=.",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "--cov-report=json:coverage.json",
        ]

        try:
            result = run_command(pytest_args, cwd=service_dir, capture_output=False)
            print(f"✅ {service_name} unit tests completed")
        except subprocess.CalledProcessError as e:
            print(f"❌ {service_name} unit tests failed with exit code {e.returncode}")
            total_exit_code = e.returncode

    return total_exit_code


def run_integration_tests_with_coverage(project_root, service_name=None):
    """Run integration tests with coverage for all services or specific service."""
    print("\n" + "=" * 60)
    print("RUNNING INTEGRATION TESTS WITH COVERAGE")
    print("=" * 60)

    # Set up environment for integration tests
    env = os.environ.copy()
    env.update(
        {
            "POSTGRES_TEST_HOST": "localhost",
            "POSTGRES_TEST_PORT": "5433",
            "POSTGRES_TEST_USER": "postgres",
            "POSTGRES_TEST_PASSWORD": "password",
            "POSTGRES_TEST_DB": "products_watch_test",
        }
    )

    # Start PostgreSQL test container
    print("🐘 Starting PostgreSQL test container...")
    try:
        run_command(
            [
                "docker-compose",
                "-f",
                "docker-compose.test.yml",
                "up",
                "-d",
                "postgres-test",
            ],
            cwd=project_root,
        )

        # Wait for PostgreSQL to be ready
        print("⏳ Waiting for PostgreSQL to be ready...")
        import time

        time.sleep(10)  # Give PostgreSQL time to start

    except Exception as e:
        print(f"⚠️ Could not start PostgreSQL container: {e}")
        print("Continuing with local PostgreSQL (make sure it's running on port 5433)")

    service_dirs = get_service_dirs(project_root)
    if service_name:
        service_dirs = [d for d in service_dirs if service_name in d]

    total_exit_code = 0

    for service_dir in service_dirs:
        service_name = os.path.basename(service_dir)
        print(f"\n🧪 Running {service_name} integration tests with coverage...")

        # Run integration tests with coverage
        pytest_args = [
            sys.executable,
            "-m",
            "pytest",
            "tests/integration",
            "-v",
            "--tb=short",
            "-m",
            "integration",
            "--cov=.",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "--cov-report=json:coverage.json",
        ]

        try:
            result = run_command(
                pytest_args, cwd=service_dir, env=env, capture_output=False
            )
            print(f"✅ {service_name} integration tests completed")
        except subprocess.CalledProcessError as e:
            print(
                f"❌ {service_name} integration tests failed with exit code {e.returncode}"
            )
            total_exit_code = e.returncode

    # Clean up containers
    try:
        run_command(
            ["docker-compose", "-f", "docker-compose.test.yml", "down", "-v"],
            cwd=project_root,
            check=False,
        )
    except Exception:
        pass

    return total_exit_code


def combine_coverage_reports(project_root):
    """Combine coverage reports from all services."""
    print("\n" + "=" * 60)
    print("COMBINING COVERAGE REPORTS")
    print("=" * 60)

    # Create a temporary directory for combined coverage
    with tempfile.TemporaryDirectory() as temp_dir:
        combined_coverage_file = os.path.join(temp_dir, "combined.coverage")

        # Collect all .coverage files
        coverage_files = []
        for service_dir in get_service_dirs(project_root):
            coverage_file = os.path.join(service_dir, ".coverage")
            if os.path.exists(coverage_file):
                coverage_files.append(coverage_file)

        if not coverage_files:
            print("❌ No coverage files found to combine")
            return False

        print(f"📊 Found {len(coverage_files)} coverage files to combine")

        # Combine coverage files
        try:
            combine_args = [
                sys.executable,
                "-m",
                "coverage",
                "combine",
            ] + coverage_files
            run_command(combine_args, cwd=temp_dir)

            # Generate combined report
            report_args = [
                sys.executable,
                "-m",
                "coverage",
                "report",
                "--show-missing",
                "--precision=2",
            ]
            print("\n📈 COMBINED COVERAGE REPORT:")
            print("-" * 50)
            run_command(report_args, cwd=temp_dir, capture_output=False)

            # Generate HTML report
            html_args = [
                sys.executable,
                "-m",
                "coverage",
                "html",
                "-d",
                "combined_htmlcov",
            ]
            run_command(html_args, cwd=temp_dir)

            # Copy combined HTML report to project root
            import shutil

            combined_html_dir = os.path.join(temp_dir, "combined_htmlcov")
            project_html_dir = os.path.join(project_root, "combined_htmlcov")

            if os.path.exists(project_html_dir):
                shutil.rmtree(project_html_dir)
            shutil.copytree(combined_html_dir, project_html_dir)

            print(
                f"\n📊 Combined HTML coverage report available at: {project_html_dir}/index.html"
            )

            # Generate XML report
            xml_args = [
                sys.executable,
                "-m",
                "coverage",
                "xml",
                "-o",
                "combined_coverage.xml",
            ]
            run_command(xml_args, cwd=temp_dir)

            # Copy XML report to project root
            xml_source = os.path.join(temp_dir, "combined_coverage.xml")
            xml_dest = os.path.join(project_root, "combined_coverage.xml")
            shutil.copy2(xml_source, xml_dest)

            print(f"📊 Combined XML coverage report available at: {xml_dest}")

            return True

        except Exception as e:
            print(f"❌ Failed to combine coverage reports: {e}")
            return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Run tests with combined coverage reporting"
    )
    parser.add_argument(
        "--unit-only", action="store_true", help="Run only unit tests with coverage"
    )
    parser.add_argument(
        "--integration-only",
        action="store_true",
        help="Run only integration tests with coverage",
    )
    parser.add_argument(
        "--service",
        choices=["product", "store", "price", "retail"],
        help="Run tests for specific service only",
    )
    parser.add_argument(
        "--no-combine", action="store_true", help="Skip combining coverage reports"
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent

    print("🚀 Starting comprehensive test coverage analysis...")

    # Clean up existing coverage files
    cleanup_coverage_files(project_root)

    total_exit_code = 0

    # Run unit tests
    if not args.integration_only:
        unit_exit_code = run_unit_tests_with_coverage(project_root, args.service)
        if unit_exit_code != 0:
            total_exit_code = unit_exit_code

    # Run integration tests
    if not args.unit_only:
        integration_exit_code = run_integration_tests_with_coverage(
            project_root, args.service
        )
        if integration_exit_code != 0:
            total_exit_code = integration_exit_code

    # Combine coverage reports
    if not args.no_combine and not args.service:
        success = combine_coverage_reports(project_root)
        if not success:
            print("⚠️ Coverage combination failed, but individual reports are available")

    # Summary
    print("\n" + "=" * 60)
    print("COVERAGE TEST SUMMARY")
    print("=" * 60)

    if total_exit_code == 0:
        print("✅ All tests passed!")
        if not args.no_combine and not args.service:
            print("📊 Combined coverage reports generated successfully")
            print("   - HTML report: combined_htmlcov/index.html")
            print("   - XML report: combined_coverage.xml")
    else:
        print(f"❌ Some tests failed with exit code {total_exit_code}")

    print("\n📋 Individual service coverage reports:")
    for service_dir in get_service_dirs(project_root):
        service_name = os.path.basename(service_dir)
        htmlcov_dir = os.path.join(service_dir, "htmlcov")
        if os.path.exists(htmlcov_dir):
            print(f"   - {service_name}: {htmlcov_dir}/index.html")

    sys.exit(total_exit_code)


if __name__ == "__main__":
    main()
