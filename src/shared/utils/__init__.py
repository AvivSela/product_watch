"""
Shared utilities for the Products Watch System.

This package contains shared utilities for Kafka communication,
database operations, and other common functionality used across services.
"""

from .kafka_consumer import KafkaConsumer, consume_kafka_messages
from .kafka_producer import KafkaProducer, send_kafka_message

__all__ = [
    "KafkaProducer",
    "KafkaConsumer",
    "send_kafka_message",
    "consume_kafka_messages",
]
