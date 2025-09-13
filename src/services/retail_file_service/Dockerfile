FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the retail file service source code
COPY src/services/retail_file_service/ .
# Copy the utils directory for kafka_producer
COPY src/utils/ ./src/utils/

# Expose port 8003
EXPOSE 8003

# Run the FastAPI application
CMD ["python", "main.py"]
