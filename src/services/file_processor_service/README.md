# File Processor Service

A simple FastAPI service for file processing operations with health check endpoints.

## Features

- Health check endpoints for monitoring service status
- Readiness and liveness checks for container orchestration
- No database dependencies
- Lightweight and fast

## Endpoints

### Health Checks

- `GET /health` - Basic health check
- `GET /health/ready` - Readiness check for Kubernetes/container orchestration
- `GET /health/live` - Liveness check for Kubernetes/container orchestration

## Running the Service

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python main.py
```

The service will be available at `http://localhost:8004`

### Docker

```bash
# Build the image
docker build -t file-processor-service .

# Run the container
docker run -p 8004:8004 file-processor-service
```

## Testing

```bash
# Run tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

## API Documentation

Once the service is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8004/docs`
- ReDoc: `http://localhost:8004/redoc`
