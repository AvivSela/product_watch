import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from aiokafka.structs import ConsumerRecord
from fastapi import FastAPI
from pydantic import BaseModel

from utils.kafka_producer import KafkaProducer

# Add the src directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from file_processor import ExtractedPriceProductItem, process_xml_file
from s3_client import S3Client

from src.utils.kafka_consumer import KafkaConsumer


# Local RetailFile model for file processor service
class RetailFile(BaseModel):
    """Retail file model for file processor service"""

    id: str
    chain_id: str
    store_id: Optional[int] = None
    file_name: str
    file_path: str
    file_size: Optional[int] = None
    upload_date: datetime
    is_processed: bool = False


# Simple message model for file processing
class RetailFileMessage(BaseModel):
    """Simple message model for retail file processing"""

    event_type: str
    data: Dict[str, Any]

    def to_retail_file_model(self) -> RetailFile:
        return RetailFile(**self.data)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to store the Kafka consumer
kafka_consumer: KafkaConsumer = None
# Global variable to store the Kafka producer
kafka_producer: KafkaProducer = None

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_PROCESSED_FILES = os.getenv(
    "KAFKA_TOPIC_PROCESSED_FILES", "processed_files"
)


async def message_handler(record: ConsumerRecord) -> None:
    """
    Handle incoming Kafka messages.

    Args:
        record: ConsumerRecord object containing the message data
    """
    try:
        # Parse the message

        message_data = kafka_consumer.parse_message(record)
        if message_data.get("value"):
            await process_file_message(RetailFileMessage(**message_data["value"]))

    except Exception as e:
        logger.error(f"Error processing message: {e}")


async def process_file_message(message_data: RetailFileMessage) -> None:
    """
    Process file-related messages from Kafka.

    Args:
        message_data: Parsed message data
    """
    try:
        # Example file processing logic

        logger.info(f"Processing message: {message_data.model_dump_json()}")

        retail_file = message_data.to_retail_file_model()

        items: List[ExtractedPriceProductItem] = process_xml_file(
            retail_file.file_path,
            retail_file.id,
            S3Client(default_bucket_name="price-files", auto_create_bucket=True),
        )

        for item in items:
            kafka_producer.send_message(
                KAFKA_TOPIC_PROCESSED_FILES,
                item.model_dump_json(),
                key=item.item_code,
            )
            logger.debug(f"Item: {item.model_dump_json()}")

    except Exception as e:
        logger.error(f"Error in file processing: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.
    Handles startup and shutdown events for the Kafka consumer.
    """
    global kafka_consumer

    # Startup
    logger.info("Starting File Processor Service...")

    try:
        # Initialize Kafka consumer

        kafka_topics = [os.getenv("KAFKA_TOPIC_RETAIL_FILES", "retail_files")]
        kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        kafka_group_id = "file-processor-group"

        kafka_consumer = KafkaConsumer(
            topics=kafka_topics,
            bootstrap_servers=kafka_servers,
            group_id=kafka_group_id,
            client_id="file-processor-service",
        )

        kafka_producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            request_timeout_ms=5000,  # 5 second timeout
            max_block_ms=5000,  # 5 second max block time,
        )

        # Connect to Kafka
        await kafka_consumer.connect()
        logger.info(f"Connected to Kafka broker at {kafka_servers}")
        logger.info(f"Subscribed to topics: {kafka_topics}")

        # Start consuming messages in the background
        consumer_task = asyncio.create_task(
            kafka_consumer.start_consuming(message_handler, poll_interval=1.0)
        )

        logger.info("File Processor Service started successfully")

    except Exception as e:
        logger.error(f"Failed to start Kafka consumer: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down File Processor Service...")

    try:
        if kafka_consumer:
            # Stop consuming messages
            kafka_consumer.stop_consuming()

            # Wait for consumer task to finish
            if "consumer_task" in locals():
                consumer_task.cancel()
                try:
                    await consumer_task
                except asyncio.CancelledError:
                    pass

            # Disconnect from Kafka
            await kafka_consumer.disconnect()

        logger.info("File Processor Service shutdown complete")

    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="File Processor Service API",
    description="A FastAPI File Processor Service with Kafka consumer for processing files",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring service status"""
    kafka_status = (
        "connected"
        if kafka_consumer and kafka_consumer.is_connected
        else "disconnected"
    )

    return {
        "status": "healthy",
        "service": "file-processor-service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "kafka_status": kafka_status,
    }


@app.get("/health/ready")
def health_check_ready():
    """Readiness check endpoint for Kubernetes/container orchestration"""
    kafka_ready = kafka_consumer and kafka_consumer.is_connected
    status = "ready" if kafka_ready else "not_ready"

    return {
        "status": status,
        "service": "file-processor-service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "kafka_connected": bool(kafka_ready),
    }


@app.get("/health/live")
def health_check_live():
    """Liveness check endpoint for Kubernetes/container orchestration"""
    return {
        "status": "alive",
        "service": "file-processor-service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI application using uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
