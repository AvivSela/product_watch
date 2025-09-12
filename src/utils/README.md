# Kafka Utilities

This directory contains utility classes for working with Apache Kafka in the products_watch application.

## Files

- `kafka_producer.py` - Async Kafka Producer utility
- `kafka_consumer.py` - Async Kafka Consumer utility
- `kafka_example.py` - Example usage of the utilities
- `test_kafka_utils.py` - Unit tests for the utilities

## Features

### KafkaProducer

- Async message production to Kafka topics
- Support for JSON, string, and bytes messages
- Batch message sending
- Automatic connection management
- Context manager support
- Error handling and retry logic

### KafkaConsumer

- Async message consumption from Kafka topics
- Support for multiple topics
- Message parsing (JSON and plain text)
- Continuous consumption with configurable limits
- Manual offset management
- Context manager support
- Error handling

## Quick Start

### Producer Example

```python
from src.utils import KafkaProducer

# Using context manager (recommended)
async with KafkaProducer(bootstrap_servers="localhost:9092") as producer:
    await producer.send_message("my_topic", {"message": "Hello Kafka!"})

# Manual connection management
producer = KafkaProducer()
await producer.connect()
await producer.send_message("my_topic", "Hello World!")
await producer.disconnect()
```

### Consumer Example

```python
from src.utils import KafkaConsumer

def message_handler(record):
    print(f"Received: {record.value.decode('utf-8')}")

# Using context manager (recommended)
async with KafkaConsumer(topics="my_topic", group_id="my_group") as consumer:
    await consumer.start_consuming(message_handler, max_messages=10)
```

### Convenience Functions

```python
from src.utils import send_kafka_message, consume_kafka_messages

# Send a single message
await send_kafka_message("my_topic", {"data": "example"})

# Consume messages
def handler(record):
    print(f"Got: {record.value}")

await consume_kafka_messages("my_topic", handler, group_id="my_group")
```

## Configuration

Both producer and consumer support extensive configuration options:

### Producer Configuration
- `bootstrap_servers`: Kafka broker addresses (default: "localhost:9092")
- `client_id`: Client identifier
- `retry_backoff_ms`: Retry delay (default: 100)
- `request_timeout_ms`: Request timeout (default: 30000)

### Consumer Configuration
- `topics`: Topic(s) to consume from
- `bootstrap_servers`: Kafka broker addresses (default: "localhost:9092")
- `group_id`: Consumer group ID
- `auto_offset_reset`: Where to start reading ("latest" or "earliest")
- `enable_auto_commit`: Auto-commit offsets (default: True)
- `session_timeout_ms`: Session timeout (default: 30000)

## Dependencies

- `aiokafka`: Async Kafka client for Python
- `pytest-asyncio`: For running async tests

## Testing

Run the unit tests:

```bash
python -m pytest src/utils/test_kafka_utils.py -v
```

## Example Usage

See `kafka_example.py` for comprehensive examples of how to use both producer and consumer utilities.

## Notes

- The utilities use `aiokafka` for async operations
- All operations are non-blocking
- Proper error handling and logging are included
- Context managers ensure proper resource cleanup
- Message parsing supports both JSON and plain text formats
