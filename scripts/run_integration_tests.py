#!/usr/bin/env python3
"""
Script to run integration tests with Docker Compose.

Supports running integration tests for store_service, product_service, price_service, and retail_file_service.
Can run all tests or specific service tests.

Usage:
  python run_integration_tests.py                    # Run all integration tests
  python run_integration_tests.py store              # Run store service tests only
  python run_integration_tests.py product            # Run product service tests only
  python run_integration_tests.py price              # Run price service tests only
  python run_integration_tests.py retail             # Run retail file service tests only
  python run_integration_tests.py local               # Run all tests locally
  python run_integration_tests.py local store         # Run store tests locally
  python run_integration_tests.py local product      # Run product tests locally
  python run_integration_tests.py local price         # Run price tests locally
  python run_integration_tests.py local retail        # Run retail tests locally
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def run_command(command, cwd=None, check=True):
    """Run a command and return the result."""
    print(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(
            command, cwd=cwd, check=check, capture_output=True, text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        raise


def cleanup_containers():
    """Clean up test containers."""
    print("🧹 Cleaning up test containers...")
    try:
        # Stop and remove test containers
        run_command(
            ["docker-compose", "-f", "docker-compose.test.yml", "down", "-v"],
            check=False,
        )

        # Remove test containers if they exist
        run_command(["docker", "rm", "-f", "products_watch_test_postgres"], check=False)
        run_command(
            ["docker", "rm", "-f", "products_watch_store_service_test"], check=False
        )
        run_command(
            ["docker", "rm", "-f", "products_watch_product_service_test"], check=False
        )
        run_command(
            ["docker", "rm", "-f", "products_watch_price_service_test"], check=False
        )
        run_command(
            ["docker", "rm", "-f", "products_watch_retail_file_service_test"],
            check=False,
        )

        print("✅ Cleanup completed")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")


def wait_for_postgres():
    """Wait for PostgreSQL to be ready."""
    print("⏳ Waiting for PostgreSQL to be ready...")
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "products_watch_test_postgres",
                    "pg_isready",
                    "-U",
                    "postgres",
                    "-d",
                    "products_watch_test",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            if "accepting connections" in result.stdout:
                print("✅ PostgreSQL is ready")
                return True
        except subprocess.CalledProcessError:
            pass

        time.sleep(2)
        print(f"Attempt {attempt + 1}/{max_attempts}...")

    print("❌ PostgreSQL did not become ready in time")
    return False


def run_tests_for_paths(test_paths, project_root, env):
    """Run pytest for given test paths."""
    test_command = (
        [
            sys.executable,
            "-m",
            "pytest",
        ]
        + test_paths
        + [
            "-v",
            "--tb=short",
            "--maxfail=5",
            "-m",
            "integration",
        ]
    )

    return subprocess.run(test_command, cwd=project_root, env=env)


def run_integration_tests(service=None):
    """Run integration tests with Docker Compose."""
    project_root = Path(__file__).parent.parent

    print("🚀 Starting integration tests...")

    try:
        # Clean up any existing containers
        cleanup_containers()

        # Start PostgreSQL test container
        print("🐘 Starting PostgreSQL test container...")
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
        if not wait_for_postgres():
            raise Exception("PostgreSQL did not become ready")

        # Set environment variables for tests
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

        # Run integration tests
        print("🧪 Running integration tests...")

        # Determine which tests to run
        if service == "store":
            test_paths = ["src/services/store_service/tests/integration"]
            print("📦 Running store service integration tests only")
            result = run_tests_for_paths(test_paths, project_root, env)
        elif service == "product":
            test_paths = ["src/services/product_service/tests/integration"]
            print("📦 Running product service integration tests only")
            result = run_tests_for_paths(test_paths, project_root, env)
        elif service == "price":
            test_paths = ["src/services/price_service/tests/integration"]
            print("📦 Running price service integration tests only")
            result = run_tests_for_paths(test_paths, project_root, env)
        elif service == "retail":
            test_paths = ["src/services/retail_file_service/tests/integration"]
            print("📦 Running retail file service integration tests only")
            result = run_tests_for_paths(test_paths, project_root, env)
        else:
            print(
                "📦 Running all integration tests (store + product + price + retail services)"
            )
            # Run store service tests first
            print("🔄 Running store service tests...")
            store_result = run_tests_for_paths(
                ["src/services/store_service/tests/integration"], project_root, env
            )

            if store_result.returncode != 0:
                print("❌ Store service tests failed")
                return store_result.returncode

            # Run product service tests
            print("🔄 Running product service tests...")
            product_result = run_tests_for_paths(
                ["src/services/product_service/tests/integration"], project_root, env
            )

            if product_result.returncode != 0:
                print("❌ Product service tests failed")
                return product_result.returncode

            # Run price service tests
            print("🔄 Running price service tests...")
            price_result = run_tests_for_paths(
                ["src/services/price_service/tests/integration"], project_root, env
            )

            if price_result.returncode != 0:
                print("❌ Price service tests failed")
                return price_result.returncode

            # Run retail file service tests
            print("🔄 Running retail file service tests...")
            retail_result = run_tests_for_paths(
                ["src/services/retail_file_service/tests/integration"],
                project_root,
                env,
            )

            if retail_result.returncode != 0:
                print("❌ Retail file service tests failed")
                return retail_result.returncode

            print("✅ All integration tests passed!")
            return 0

        if result.returncode == 0:
            print("✅ All integration tests passed!")
        else:
            print(f"❌ Integration tests failed with exit code {result.returncode}")

        return result.returncode

    except Exception as e:
        print(f"❌ Integration test setup failed: {e}")
        return 1

    finally:
        # Clean up
        cleanup_containers()


def run_integration_tests_locally(service=None):
    """Run integration tests locally (without Docker Compose)."""
    project_root = Path(__file__).parent.parent

    print("🧪 Running integration tests locally...")
    print("Note: Make sure PostgreSQL test container is running on port 5433")

    # Set environment variables for tests
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

    # Determine which tests to run
    if service == "store":
        test_paths = ["src/services/store_service/tests/integration"]
        print("📦 Running store service integration tests only")
        result = run_tests_for_paths(test_paths, project_root, env)
    elif service == "product":
        test_paths = ["src/services/product_service/tests/integration"]
        print("📦 Running product service integration tests only")
        result = run_tests_for_paths(test_paths, project_root, env)
    elif service == "price":
        test_paths = ["src/services/price_service/tests/integration"]
        print("📦 Running price service integration tests only")
        result = run_tests_for_paths(test_paths, project_root, env)
    elif service == "retail":
        test_paths = ["src/services/retail_file_service/tests/integration"]
        print("📦 Running retail file service integration tests only")
        result = run_tests_for_paths(test_paths, project_root, env)
    else:
        print(
            "📦 Running all integration tests (store + product + price + retail services)"
        )
        # Run store service tests first
        print("🔄 Running store service tests...")
        store_result = run_tests_for_paths(
            ["src/services/store_service/tests/integration"], project_root, env
        )

        if store_result.returncode != 0:
            print("❌ Store service tests failed")
            return store_result.returncode

        # Run product service tests
        print("🔄 Running product service tests...")
        product_result = run_tests_for_paths(
            ["src/services/product_service/tests/integration"], project_root, env
        )

        if product_result.returncode != 0:
            print("❌ Product service tests failed")
            return product_result.returncode

        # Run price service tests
        print("🔄 Running price service tests...")
        price_result = run_tests_for_paths(
            ["src/services/price_service/tests/integration"], project_root, env
        )

        if price_result.returncode != 0:
            print("❌ Price service tests failed")
            return price_result.returncode

        # Run retail file service tests
        print("🔄 Running retail file service tests...")
        retail_result = run_tests_for_paths(
            ["src/services/retail_file_service/tests/integration"], project_root, env
        )

        if retail_result.returncode != 0:
            print("❌ Retail file service tests failed")
            return retail_result.returncode

        print("✅ All integration tests passed!")
        return 0

    if result.returncode == 0:
        print("✅ All integration tests passed!")
    else:
        print(f"❌ Integration tests failed with exit code {result.returncode}")

    return result.returncode


def main():
    """Main function."""
    service = None

    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "local":
            # Check for service parameter
            if len(sys.argv) > 2:
                service = sys.argv[2]
            exit_code = run_integration_tests_locally(service)
        elif sys.argv[1] in ["store", "product", "price", "retail"]:
            # Service specified without local
            service = sys.argv[1]
            exit_code = run_integration_tests(service)
        else:
            print("Usage:")
            print(
                "  python run_integration_tests.py                    # Run all integration tests"
            )
            print(
                "  python run_integration_tests.py store              # Run store service tests only"
            )
            print(
                "  python run_integration_tests.py product            # Run product service tests only"
            )
            print(
                "  python run_integration_tests.py price              # Run price service tests only"
            )
            print(
                "  python run_integration_tests.py retail             # Run retail file service tests only"
            )
            print(
                "  python run_integration_tests.py local               # Run all tests locally"
            )
            print(
                "  python run_integration_tests.py local store         # Run store tests locally"
            )
            print(
                "  python run_integration_tests.py local product      # Run product tests locally"
            )
            print(
                "  python run_integration_tests.py local price         # Run price tests locally"
            )
            print(
                "  python run_integration_tests.py local retail        # Run retail tests locally"
            )
            sys.exit(1)
    else:
        exit_code = run_integration_tests()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
