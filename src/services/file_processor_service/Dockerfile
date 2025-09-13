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

# Copy the file processor service source code
COPY src/services/file_processor_service/ .

# Expose port 8004
EXPOSE 8004

# Run the FastAPI application
CMD ["python", "main.py"]
