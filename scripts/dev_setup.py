#!/usr/bin/env python3
"""
Development setup script for Products Watch System.
"""

import subprocess
import sys


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)


def main():
    """Main setup function."""
    print("🚀 Setting up Products Watch System for development...")

    # Install package in development mode
    run_command("pip install -e .", "Installing package in development mode")

    # Install development dependencies
    run_command(
        "pip install pytest pytest-asyncio pytest-cov",
        "Installing development dependencies",
    )

    print("🎉 Development setup complete!")
    print("\nYou can now:")
    print("  - Run tests: pytest")
    print("  - Start services: docker-compose up")
    print(
        "  - Import modules from anywhere: from utils.kafka_producer import KafkaProducer"
    )


if __name__ == "__main__":
    main()
