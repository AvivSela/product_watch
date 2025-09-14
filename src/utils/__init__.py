"""
Utility modules for the Products Watch System.

This package contains shared utilities for Kafka communication,
database operations, and other common functionality.
"""

from .kafka_consumer import KafkaConsumer
from .kafka_producer import KafkaProducer

__all__ = ["KafkaProducer", "KafkaConsumer"]
