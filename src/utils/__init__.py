"""
Utils package for products_watch application.

This package contains utility modules for common functionality across services.
"""

from .kafka_consumer import KafkaConsumer, consume_kafka_messages
from .kafka_producer import KafkaProducer, send_kafka_message

__all__ = [
    "KafkaProducer",
    "KafkaConsumer",
    "send_kafka_message",
    "consume_kafka_messages",
]
