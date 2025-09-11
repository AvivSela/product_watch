#!/usr/bin/env python3
"""
Script to run integration tests with Docker Compose.
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


def run_integration_tests():
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
        test_command = [
            sys.executable,
            "-m",
            "pytest",
            "src/services/store_service/tests/integration",
            "-v",
            "--tb=short",
            "--maxfail=5",
        ]

        result = subprocess.run(test_command, cwd=project_root, env=env)

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


def run_integration_tests_locally():
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

    # Run integration tests
    test_command = [
        sys.executable,
        "-m",
        "pytest",
        "src/services/store_service/tests/integration",
        "-v",
        "--tb=short",
        "--maxfail=5",
    ]

    result = subprocess.run(test_command, cwd=project_root, env=env)

    if result.returncode == 0:
        print("✅ All integration tests passed!")
    else:
        print(f"❌ Integration tests failed with exit code {result.returncode}")

    return result.returncode


def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "local":
        exit_code = run_integration_tests_locally()
    else:
        exit_code = run_integration_tests()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
