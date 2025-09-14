"""
Simple tests for Kafka utilities.

These tests verify that the Kafka utilities can be imported and instantiated correctly.
Note: These are basic unit tests that don't require a running Kafka broker.
"""

# Standard library imports
from unittest.mock import MagicMock

# Third-party imports
import pytest

# Local application imports
from .kafka_consumer import KafkaConsumer, consume_kafka_messages
from .kafka_producer import KafkaProducer, send_kafka_message


class TestKafkaProducer:
    """Test cases for KafkaProducer class."""

    def test_producer_initialization(self):
        """Test that producer can be initialized with default parameters."""
        producer = KafkaProducer()
        assert producer.bootstrap_servers == "localhost:9092"
        assert producer.client_id is not None
        assert producer._is_connected is False
        assert producer.producer is None

    def test_producer_initialization_with_custom_params(self):
        """Test that producer can be initialized with custom parameters."""
        producer = KafkaProducer(
            bootstrap_servers="kafka:9092",
            client_id="test_producer",
            retry_backoff_ms=200,
        )
        assert producer.bootstrap_servers == "kafka:9092"
        assert producer.client_id == "test_producer"
        assert producer.config["retry_backoff_ms"] == 200

    @pytest.mark.asyncio
    async def test_producer_context_manager(self):
        """Test that producer works as async context manager."""
        producer = KafkaProducer()

        # Test that the context manager returns the producer instance
        async with producer as p:
            assert p is producer
            # The producer should be marked as connected (even if connection fails)
            # We can't easily mock the Kafka connection without complex setup

    def test_is_connected_property(self):
        """Test the is_connected property."""
        producer = KafkaProducer()
        assert producer.is_connected is False

        producer._is_connected = True
        assert producer.is_connected is True


class TestKafkaConsumer:
    """Test cases for KafkaConsumer class."""

    def test_consumer_initialization_single_topic(self):
        """Test that consumer can be initialized with a single topic."""
        consumer = KafkaConsumer(topics="test_topic")
        assert consumer.topics == ["test_topic"]
        assert consumer.bootstrap_servers == "localhost:9092"
        assert consumer._is_connected is False
        assert consumer.consumer is None

    def test_consumer_initialization_multiple_topics(self):
        """Test that consumer can be initialized with multiple topics."""
        topics = ["topic1", "topic2", "topic3"]
        consumer = KafkaConsumer(topics=topics)
        assert consumer.topics == topics

    def test_consumer_initialization_with_custom_params(self):
        """Test that consumer can be initialized with custom parameters."""
        consumer = KafkaConsumer(
            topics="test_topic",
            bootstrap_servers="kafka:9092",
            group_id="test_group",
            auto_offset_reset="earliest",
        )
        assert consumer.bootstrap_servers == "kafka:9092"
        assert consumer.group_id == "test_group"
        assert consumer.config["auto_offset_reset"] == "earliest"

    @pytest.mark.asyncio
    async def test_consumer_context_manager(self):
        """Test that consumer works as async context manager."""
        consumer = KafkaConsumer(topics="test_topic")

        # Test that the context manager returns the consumer instance
        async with consumer as c:
            assert c is consumer
            # The consumer should be marked as connected (even if connection fails)
            # We can't easily mock the Kafka connection without complex setup

    def test_is_connected_property(self):
        """Test the is_connected property."""
        consumer = KafkaConsumer(topics="test_topic")
        assert consumer.is_connected is False

        consumer._is_connected = True
        assert consumer.is_connected is True

    def test_is_running_property(self):
        """Test the is_running property."""
        consumer = KafkaConsumer(topics="test_topic")
        assert consumer.is_running is False

        consumer._running = True
        assert consumer.is_running is True

    def test_parse_message(self):
        """Test message parsing functionality."""
        consumer = KafkaConsumer(topics="test_topic")

        # Create a mock ConsumerRecord
        mock_record = MagicMock()
        mock_record.topic = "test_topic"
        mock_record.partition = 0
        mock_record.offset = 123
        mock_record.timestamp = 1640995200000
        mock_record.key = b"test_key"
        mock_record.value = b'{"message": "test"}'
        mock_record.headers = []

        parsed = consumer.parse_message(mock_record)

        assert parsed["topic"] == "test_topic"
        assert parsed["partition"] == 0
        assert parsed["offset"] == 123
        assert parsed["key"] == "test_key"
        assert parsed["value"] == {"message": "test"}


class TestConvenienceFunctions:
    """Test cases for convenience functions."""

    def test_send_kafka_message_function_exists(self):
        """Test that send_kafka_message function exists and is callable."""
        assert callable(send_kafka_message)

    def test_consume_kafka_messages_function_exists(self):
        """Test that consume_kafka_messages function exists and is callable."""
        assert callable(consume_kafka_messages)


if __name__ == "__main__":
    pytest.main([__file__])
