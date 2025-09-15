#!/usr/bin/env python3
"""
Script to run linting checks locally.
This script runs the same checks that are performed in the GitHub Actions workflow.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and return success status."""
    print(f"\n🔍 {description}...")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"✅ {description} passed!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def check_todo_comments():
    """Check for TODO/FIXME comments in source code."""
    print("\n🔍 Checking for TODO/FIXME comments...")
    src_dir = Path("src")
    if not src_dir.exists():
        print("❌ src/ directory not found!")
        return False

    todo_files = []
    for py_file in src_dir.rglob("*.py"):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
                if "TODO" in content or "FIXME" in content:
                    todo_files.append(str(py_file))
        except Exception as e:
            print(f"Warning: Could not read {py_file}: {e}")

    if todo_files:
        print("❌ Found TODO/FIXME comments in the following files:")
        for file in todo_files:
            print(f"  - {file}")
        return False
    else:
        print("✅ No TODO/FIXME comments found.")
        return True


def main():
    """Run all linting checks."""
    print("🚀 Running linting checks...")

    # Change to project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)

    checks = [
        (["ruff", "check", "src/", "--output-format=concise"], "Ruff linter"),
        (["ruff", "format", "--check", "src/"], "Ruff formatter check"),
        (
            [
                "mypy",
                "src/",
                "--ignore-missing-imports",
                "--show-error-codes",
                "--no-strict-optional",
            ],
            "MyPy type checker",
        ),
    ]

    all_passed = True

    for command, description in checks:
        if not run_command(command, description):
            all_passed = False

    # Check for TODO/FIXME comments
    if not check_todo_comments():
        all_passed = False

    if all_passed:
        print("\n🎉 All linting checks passed!")
        return 0
    else:
        print("\n💥 Some linting checks failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
