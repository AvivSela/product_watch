FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the main requirements file first
COPY requirements.txt .

# Copy the file processor service requirements
COPY src/services/file_processor_service/requirements.txt ./service_requirements.txt

# Install Python dependencies from both requirements files
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r service_requirements.txt

# Copy the entire source code structure
COPY src/ ./src/

# Copy the file processor service source code
COPY src/services/file_processor_service/ .

# Expose port 8004
EXPOSE 8004

# Run the FastAPI application
CMD ["python", "main.py"]
