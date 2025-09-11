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

# Copy the product service source code
COPY src/services/product_service/ .

# Expose port 8001
EXPOSE 8001

# Run the FastAPI application
CMD ["python", "main.py"]
