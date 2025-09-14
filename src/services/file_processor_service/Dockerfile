FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire project first
COPY . /app

# Install the project as an editable package
RUN pip install -e .

# Copy service-specific requirements and install them
COPY src/services/file_processor_service/requirements.txt ./service_requirements.txt
RUN pip install --no-cache-dir -r service_requirements.txt

# Copy service files to working directory
COPY src/services/file_processor_service/ .

# Expose port 8004
EXPOSE 8004

# Run the FastAPI application
CMD ["python", "main.py"]
