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

# Copy the store service source code
COPY src/services/store_service/ .

# Expose port 8000
EXPOSE 8000

# Run the FastAPI application
CMD ["python", "main.py"]
