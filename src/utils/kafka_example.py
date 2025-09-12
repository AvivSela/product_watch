"""
Example usage of Kafka Producer and Consumer utilities.

This script demonstrates how to use the Kafka utilities for sending and receiving messages.
"""

import asyncio
import json
import logging

from aiokafka.structs import ConsumerRecord

from .kafka_consumer import KafkaConsumer
from .kafka_producer import KafkaProducer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_producer():
    """Example of using the Kafka Producer."""
    logger.info("=== Kafka Producer Example ===")

    # Create producer instance
    producer = KafkaProducer(
        bootstrap_servers="localhost:9092", client_id="example_producer"
    )

    try:
        # Connect to Kafka
        await producer.connect()

        # Send a simple message
        message = {
            "type": "test",
            "content": "Hello Kafka!",
            "timestamp": "2024-01-01T00:00:00Z",
        }
        success = await producer.send_message("test_topic", message)

        if success:
            logger.info("Message sent successfully!")
        else:
            logger.error("Failed to send message")

        # Send multiple messages
        messages = [
            {"id": 1, "name": "Product A", "price": 10.99},
            {"id": 2, "name": "Product B", "price": 20.99},
            {"id": 3, "name": "Product C", "price": 30.99},
        ]

        sent_count = await producer.send_batch(
            "products_topic", messages, key_field="id"
        )
        logger.info(f"Sent {sent_count} product messages")

    finally:
        # Disconnect
        await producer.disconnect()


async def example_consumer():
    """Example of using the Kafka Consumer."""
    logger.info("=== Kafka Consumer Example ===")

    def message_handler(record: ConsumerRecord) -> None:
        """Handle incoming messages."""
        logger.info(f"Received message from topic '{record.topic}':")
        logger.info(f"  Partition: {record.partition}")
        logger.info(f"  Offset: {record.offset}")
        logger.info(f"  Key: {record.key}")

        try:
            message_data = json.loads(record.value.decode("utf-8"))
            logger.info(f"  Value: {message_data}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.info(f"  Value: {record.value}")

    # Create consumer instance
    consumer = KafkaConsumer(
        topics=["test_topic", "products_topic"],
        bootstrap_servers="localhost:9092",
        group_id="example_consumer_group",
        auto_offset_reset="earliest",
    )

    try:
        # Connect to Kafka
        await consumer.connect()

        # Consume messages for a limited time
        logger.info("Starting to consume messages...")
        await consumer.start_consuming(message_handler, max_messages=10)

    finally:
        # Disconnect
        await consumer.disconnect()


async def example_context_manager():
    """Example using context managers."""
    logger.info("=== Context Manager Example ===")

    # Producer with context manager
    async with KafkaProducer(bootstrap_servers="localhost:9092") as producer:
        await producer.send_message(
            "context_topic", {"message": "Using context manager!"}
        )
        logger.info("Message sent using context manager")

    # Consumer with context manager
    def simple_handler(record: ConsumerRecord) -> None:
        logger.info(f"Context manager received: {record.value.decode('utf-8')}")

    async with KafkaConsumer(
        topics="context_topic",
        bootstrap_servers="localhost:9092",
        group_id="context_group",
    ) as consumer:
        # Consume a few messages
        records = await consumer.consume_messages(simple_handler, timeout_ms=5000)
        logger.info(f"Consumed {len(records)} messages using context manager")


async def main():
    """Main function to run all examples."""
    logger.info("Starting Kafka utilities examples...")

    try:
        # Run producer example
        await example_producer()

        # Wait a bit
        await asyncio.sleep(2)

        # Run consumer example
        await example_consumer()

        # Wait a bit
        await asyncio.sleep(2)

        # Run context manager example
        await example_context_manager()

    except Exception as e:
        logger.error(f"Error running examples: {e}")

    logger.info("Examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
