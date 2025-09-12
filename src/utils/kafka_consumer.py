"""
Kafka Consumer Utility

This module provides a utility class for consuming messages from Kafka topics.
It uses aiokafka for async operations and includes error handling and message processing.
"""

import asyncio
import json
import logging
from typing import Any, Callable, Dict, List, Optional, Union

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
from aiokafka.structs import ConsumerRecord

logger = logging.getLogger(__name__)


class KafkaConsumer:
    """
    Async Kafka Consumer utility class.

    Provides methods to consume messages from Kafka topics with proper error handling
    and message processing callbacks.
    """

    def __init__(
        self,
        topics: Union[str, List[str]],
        bootstrap_servers: str = "localhost:9092",
        group_id: Optional[str] = None,
        client_id: Optional[str] = None,
        auto_offset_reset: str = "latest",
        enable_auto_commit: bool = True,
        auto_commit_interval_ms: int = 5000,
        session_timeout_ms: int = 30000,
        heartbeat_interval_ms: int = 3000,
        max_poll_records: int = 500,
        **kwargs,
    ):
        """
        Initialize the Kafka Consumer.

        Args:
            topics: Topic(s) to consume from
            bootstrap_servers: Kafka broker addresses (default: localhost:9092)
            group_id: Consumer group ID
            client_id: Client identifier for this consumer
            auto_offset_reset: Where to start reading when no offset exists
            enable_auto_commit: Whether to auto-commit offsets
            auto_commit_interval_ms: Auto-commit interval in milliseconds
            session_timeout_ms: Session timeout in milliseconds
            heartbeat_interval_ms: Heartbeat interval in milliseconds
            max_poll_records: Maximum number of records to poll at once
            **kwargs: Additional consumer configuration options
        """
        self.topics = topics if isinstance(topics, list) else [topics]
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id or f"consumer_group_{id(self)}"
        self.client_id = client_id or f"consumer_{id(self)}"
        self.consumer: Optional[AIOKafkaConsumer] = None
        self._is_connected = False
        self._running = False

        # Consumer configuration
        self.config = {
            "bootstrap_servers": bootstrap_servers,
            "group_id": self.group_id,
            "client_id": self.client_id,
            "auto_offset_reset": auto_offset_reset,
            "enable_auto_commit": enable_auto_commit,
            "auto_commit_interval_ms": auto_commit_interval_ms,
            "session_timeout_ms": session_timeout_ms,
            "heartbeat_interval_ms": heartbeat_interval_ms,
            "max_poll_records": max_poll_records,
            **kwargs,
        }

    async def connect(self) -> None:
        """Establish connection to Kafka broker."""
        if self._is_connected:
            logger.warning("Consumer is already connected")
            return

        try:
            self.consumer = AIOKafkaConsumer(*self.topics, **self.config)
            await self.consumer.start()
            self._is_connected = True
            logger.info(f"Connected to Kafka broker at {self.bootstrap_servers}")
            logger.info(f"Subscribed to topics: {self.topics}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise

    async def disconnect(self) -> None:
        """Close connection to Kafka broker."""
        if not self._is_connected or not self.consumer:
            return

        try:
            self._running = False
            await self.consumer.stop()
            self._is_connected = False
            logger.info("Disconnected from Kafka broker")
        except Exception as e:
            logger.error(f"Error disconnecting from Kafka: {e}")

    async def consume_messages(
        self,
        message_handler: Callable[[ConsumerRecord], Any],
        timeout_ms: int = 1000,
        max_records: Optional[int] = None,
    ) -> List[ConsumerRecord]:
        """
        Consume messages from subscribed topics.

        Args:
            message_handler: Function to handle each message
            timeout_ms: Timeout for polling messages
            max_records: Maximum number of records to consume (None for unlimited)

        Returns:
            List of consumed ConsumerRecord objects
        """
        if not self._is_connected or not self.consumer:
            logger.error("Consumer is not connected")
            return []

        try:
            messages = await self.consumer.getmany(
                timeout_ms=timeout_ms, max_records=max_records
            )
            consumed_records = []

            for topic_partition, records in messages.items():
                for record in records:
                    try:
                        # Call the message handler
                        await self._handle_message(record, message_handler)
                        consumed_records.append(record)
                    except Exception as e:
                        logger.error(
                            f"Error handling message from {topic_partition}: {e}"
                        )

            return consumed_records

        except KafkaError as e:
            logger.error(f"Kafka error consuming messages: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error consuming messages: {e}")
            return []

    async def _handle_message(
        self, record: ConsumerRecord, message_handler: Callable[[ConsumerRecord], Any]
    ) -> None:
        """Handle a single message record."""
        try:
            # Check if handler is async
            if asyncio.iscoroutinefunction(message_handler):
                await message_handler(record)
            else:
                message_handler(record)
        except Exception as e:
            logger.error(f"Error in message handler: {e}")
            raise

    async def start_consuming(
        self,
        message_handler: Callable[[ConsumerRecord], Any],
        poll_interval: float = 1.0,
        max_messages: Optional[int] = None,
    ) -> None:
        """
        Start continuous message consumption.

        Args:
            message_handler: Function to handle each message
            poll_interval: Interval between polls in seconds
            max_messages: Maximum number of messages to consume (None for unlimited)
        """
        if not self._is_connected or not self.consumer:
            logger.error("Consumer is not connected")
            return

        self._running = True
        message_count = 0

        logger.info(f"Starting to consume messages from topics: {self.topics}")

        try:
            while self._running:
                if max_messages and message_count >= max_messages:
                    logger.info(f"Reached maximum message limit: {max_messages}")
                    break

                records = await self.consume_messages(message_handler)
                message_count += len(records)

                if not records:
                    await asyncio.sleep(poll_interval)

        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping consumer...")
        except Exception as e:
            logger.error(f"Error during message consumption: {e}")
        finally:
            self._running = False
            logger.info(f"Stopped consuming messages. Total processed: {message_count}")

    def stop_consuming(self) -> None:
        """Stop the continuous message consumption."""
        self._running = False
        logger.info("Stop signal sent to consumer")

    async def commit_offsets(self) -> None:
        """Manually commit current offsets."""
        if not self._is_connected or not self.consumer:
            logger.error("Consumer is not connected")
            return

        try:
            await self.consumer.commit()
            logger.debug("Offsets committed successfully")
        except Exception as e:
            logger.error(f"Error committing offsets: {e}")

    def parse_message(self, record: ConsumerRecord) -> Dict[str, Any]:
        """
        Parse a consumer record into a dictionary.

        Args:
            record: ConsumerRecord object

        Returns:
            Dictionary containing parsed message data
        """
        try:
            # Decode the message value
            if record.value:
                try:
                    # Try to parse as JSON first
                    message_data = json.loads(record.value.decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # If not JSON, treat as plain text
                    message_data = record.value.decode("utf-8")
            else:
                message_data = None

            # Decode the key if present
            key_data = None
            if record.key:
                try:
                    key_data = record.key.decode("utf-8")
                except UnicodeDecodeError:
                    key_data = record.key

            return {
                "topic": record.topic,
                "partition": record.partition,
                "offset": record.offset,
                "timestamp": record.timestamp,
                "key": key_data,
                "value": message_data,
                "headers": dict(record.headers) if record.headers else {},
            }
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return {
                "topic": record.topic,
                "partition": record.partition,
                "offset": record.offset,
                "timestamp": record.timestamp,
                "key": record.key,
                "value": record.value,
                "headers": dict(record.headers) if record.headers else {},
                "parse_error": str(e),
            }

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    @property
    def is_connected(self) -> bool:
        """Check if consumer is connected."""
        return self._is_connected

    @property
    def is_running(self) -> bool:
        """Check if consumer is actively consuming."""
        return self._running


# Convenience function for quick message consumption
async def consume_kafka_messages(
    topics: Union[str, List[str]],
    message_handler: Callable[[ConsumerRecord], Any],
    bootstrap_servers: str = "localhost:9092",
    group_id: Optional[str] = None,
    max_messages: Optional[int] = None,
    **kwargs,
) -> None:
    """
    Convenience function to consume messages from Kafka.

    Args:
        topics: Topic(s) to consume from
        message_handler: Function to handle each message
        bootstrap_servers: Kafka broker addresses
        group_id: Consumer group ID
        max_messages: Maximum number of messages to consume
        **kwargs: Additional consumer configuration
    """
    async with KafkaConsumer(
        topics=topics, bootstrap_servers=bootstrap_servers, group_id=group_id, **kwargs
    ) as consumer:
        await consumer.start_consuming(message_handler, max_messages=max_messages)
