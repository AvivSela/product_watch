"""
Kafka Producer Utility

This module provides a utility class for producing messages to Kafka topics.
It uses aiokafka for async operations and includes error handling and retry logic.
"""

import json
import logging
from typing import Any, Dict, Optional, Union

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

logger = logging.getLogger(__name__)


class KafkaProducer:
    """
    Async Kafka Producer utility class.

    Provides methods to send messages to Kafka topics with proper error handling
    and connection management.
    """

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        client_id: Optional[str] = None,
        retry_backoff_ms: int = 100,
        max_block_ms: int = 60000,
        request_timeout_ms: int = 30000,
        **kwargs,
    ):
        """
        Initialize the Kafka Producer.

        Args:
            bootstrap_servers: Kafka broker addresses (default: localhost:9092)
            client_id: Client identifier for this producer
            retry_backoff_ms: Time to wait before retrying failed requests
            max_block_ms: Maximum time to block when buffer is full
            request_timeout_ms: Request timeout in milliseconds
            **kwargs: Additional producer configuration options
        """
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id or f"producer_{id(self)}"
        self.producer: Optional[AIOKafkaProducer] = None
        self._is_connected = False

        # Producer configuration
        self.config = {
            "bootstrap_servers": bootstrap_servers,
            "client_id": self.client_id,
            "retry_backoff_ms": retry_backoff_ms,
            "request_timeout_ms": request_timeout_ms,
            **kwargs,
        }

    async def connect(self) -> None:
        """Establish connection to Kafka broker."""
        if self._is_connected:
            logger.warning("Producer is already connected")
            return

        try:
            self.producer = AIOKafkaProducer(**self.config)
            await self.producer.start()
            self._is_connected = True
            logger.info(f"Connected to Kafka broker at {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise

    async def disconnect(self) -> None:
        """Close connection to Kafka broker."""
        if not self._is_connected or not self.producer:
            return

        try:
            await self.producer.stop()
            self._is_connected = False
            logger.info("Disconnected from Kafka broker")
        except Exception as e:
            logger.error(f"Error disconnecting from Kafka: {e}")

    async def send_message(
        self,
        topic: str,
        message: Union[str, bytes, Dict[str, Any]],
        key: Optional[Union[str, bytes]] = None,
        partition: Optional[int] = None,
        timestamp_ms: Optional[int] = None,
    ) -> bool:
        """
        Send a message to a Kafka topic.

        Args:
            topic: Target Kafka topic
            message: Message content (str, bytes, or dict)
            key: Optional message key for partitioning
            partition: Optional specific partition to send to
            timestamp_ms: Optional timestamp in milliseconds

        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        if not self._is_connected or not self.producer:
            logger.error("Producer is not connected")
            return False

        try:
            # Serialize message if it's a dict
            if isinstance(message, dict):
                message_bytes = json.dumps(message).encode("utf-8")
            elif isinstance(message, str):
                message_bytes = message.encode("utf-8")
            else:
                message_bytes = message

            # Serialize key if provided
            key_bytes = None
            if key is not None:
                if isinstance(key, str):
                    key_bytes = key.encode("utf-8")
                else:
                    key_bytes = key

            # Send the message
            await self.producer.send_and_wait(
                topic=topic,
                value=message_bytes,
                key=key_bytes,
                partition=partition,
                timestamp_ms=timestamp_ms,
            )

            logger.debug(f"Message sent to topic '{topic}' successfully")
            return True

        except KafkaError as e:
            logger.error(f"Kafka error sending message to topic '{topic}': {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message to topic '{topic}': {e}")
            return False

    async def send_batch(
        self, topic: str, messages: list, key_field: Optional[str] = None
    ) -> int:
        """
        Send multiple messages to a Kafka topic in batch.

        Args:
            topic: Target Kafka topic
            messages: List of messages to send
            key_field: Optional field name to use as message key

        Returns:
            int: Number of messages sent successfully
        """
        if not self._is_connected or not self.producer:
            logger.error("Producer is not connected")
            return 0

        sent_count = 0

        for message in messages:
            key = None
            if key_field and isinstance(message, dict) and key_field in message:
                key = message[key_field]

            success = await self.send_message(topic, message, key)
            if success:
                sent_count += 1

        logger.info(f"Sent {sent_count}/{len(messages)} messages to topic '{topic}'")
        return sent_count

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    @property
    def is_connected(self) -> bool:
        """Check if producer is connected."""
        return self._is_connected


# Convenience function for quick message sending
async def send_kafka_message(
    topic: str,
    message: Union[str, bytes, Dict[str, Any]],
    bootstrap_servers: str = "localhost:9092",
    key: Optional[Union[str, bytes]] = None,
    **kwargs,
) -> bool:
    """
    Convenience function to send a single message to Kafka.

    Args:
        topic: Target Kafka topic
        message: Message content
        bootstrap_servers: Kafka broker addresses
        key: Optional message key
        **kwargs: Additional producer configuration

    Returns:
        bool: True if message was sent successfully
    """
    async with KafkaProducer(bootstrap_servers=bootstrap_servers, **kwargs) as producer:
        return await producer.send_message(topic, message, key)
