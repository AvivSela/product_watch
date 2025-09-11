#!/usr/bin/env python3
"""
Quick test script to verify integration test setup.
"""

import subprocess
import sys


def test_postgres_container():
    """Test if PostgreSQL container can be started."""
    print("🐘 Testing PostgreSQL container setup...")

    try:
        # Try to start the container
        result = subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                "test_postgres_integration",
                "-p",
                "5434:5432",
                "-e",
                "POSTGRES_DB=test_db",
                "-e",
                "POSTGRES_USER=postgres",
                "-e",
                "POSTGRES_PASSWORD=password",
                "postgres:15-alpine",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        print("✅ PostgreSQL container started successfully")

        # Wait a bit for it to be ready
        import time

        time.sleep(5)

        # Test connection
        result = subprocess.run(
            [
                "docker",
                "exec",
                "test_postgres_integration",
                "pg_isready",
                "-U",
                "postgres",
                "-d",
                "test_db",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        print("✅ PostgreSQL is ready and accepting connections")

        # Clean up
        subprocess.run(["docker", "rm", "-f", "test_postgres_integration"], check=False)
        print("✅ Container cleaned up")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ PostgreSQL container test failed: {e}")
        # Clean up on failure
        subprocess.run(["docker", "rm", "-f", "test_postgres_integration"], check=False)
        return False


def test_python_dependencies():
    """Test if required Python packages are available."""
    print("🐍 Testing Python dependencies...")

    required_packages = [
        ("pytest", "pytest"),
        ("fastapi", "fastapi"),
        ("sqlalchemy", "sqlalchemy"),
        ("psycopg2-binary", "psycopg2"),
    ]

    missing_packages = []

    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name} is available")
        except ImportError:
            print(f"❌ {package_name} is missing")
            missing_packages.append(package_name)

    if missing_packages:
        print(f"\n⚠️ Missing packages: {missing_packages}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False

    return True


def test_docker_availability():
    """Test if Docker is available."""
    print("🐳 Testing Docker availability...")

    try:
        result = subprocess.run(
            ["docker", "--version"], capture_output=True, text=True, check=True
        )
        print(f"✅ Docker is available: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("❌ Docker is not available or not running")
        return False


def main():
    """Run all tests."""
    print("🧪 Integration Test Setup Verification")
    print("=" * 50)

    tests = [
        ("Docker", test_docker_availability),
        ("Python Dependencies", test_python_dependencies),
        ("PostgreSQL Container", test_postgres_container),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("SUMMARY:")

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 All tests passed! Integration test setup is ready.")
        print("\nNext steps:")
        print("1. Run: python run_all_tests.py --type integration")
        print("2. Or run: python scripts/run_integration_tests.py")
    else:
        print("\n💥 Some tests failed. Please fix the issues above.")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
