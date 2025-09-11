#!/usr/bin/env python3
"""
Example script demonstrating how to run integration tests.
This shows the basic usage patterns for the integration test setup.
"""

import subprocess
import sys
from pathlib import Path


def run_example():
    """Run a simple example of the integration tests."""
    project_root = Path(__file__).parent.parent

    print("🚀 Integration Test Example")
    print("=" * 50)

    print("\n1. Running unit tests first (for comparison)...")
    try:
        result = subprocess.run(
            [sys.executable, "run_all_tests.py", "--type", "unit"],
            cwd=project_root,
            check=True,
        )
        print("✅ Unit tests completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Unit tests failed: {e}")
        return 1

    print("\n2. Running integration tests...")
    print("   This will:")
    print("   - Start a PostgreSQL container")
    print("   - Run tests against real database")
    print("   - Clean up containers")

    try:
        result = subprocess.run(
            [sys.executable, "run_all_tests.py", "--type", "integration"],
            cwd=project_root,
            check=True,
        )
        print("✅ Integration tests completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Integration tests failed: {e}")
        return 1

    print("\n3. Running all tests together...")
    try:
        result = subprocess.run(
            [sys.executable, "run_all_tests.py", "--type", "all"],
            cwd=project_root,
            check=True,
        )
        print("✅ All tests completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Some tests failed: {e}")
        return 1

    print("\n🎉 Example completed successfully!")
    print("\nNext steps:")
    print(
        "- Check the integration test files in src/services/store_service/tests/integration/"
    )
    print("- Modify tests to match your specific requirements")
    print("- Add integration tests for other services")
    print("- Integrate with your CI/CD pipeline")

    return 0


def show_help():
    """Show help information."""
    print("Integration Test Example")
    print("=" * 50)
    print("\nThis script demonstrates how to run integration tests.")
    print("\nAvailable commands:")
    print("  python scripts/example_integration_test.py run    - Run the example")
    print("  python scripts/example_integration_test.py help    - Show this help")
    print("\nManual commands:")
    print("  python run_all_tests.py --type unit         - Run unit tests only")
    print("  python run_all_tests.py --type integration  - Run integration tests only")
    print("  python run_all_tests.py --type all          - Run all tests")
    print("\nDirect integration test commands:")
    print(
        "  python scripts/run_integration_tests.py           - Run with Docker Compose"
    )
    print(
        "  python scripts/run_integration_tests.py local    - Run locally (manual setup)"
    )


def main():
    """Main function."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "help":
            show_help()
            return 0
        elif command == "run":
            return run_example()
        else:
            print(f"Unknown command: {command}")
            show_help()
            return 1
    else:
        show_help()
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
