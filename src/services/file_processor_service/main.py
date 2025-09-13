from datetime import datetime, timezone

from fastapi import FastAPI

# Initialize FastAPI app
app = FastAPI(
    title="File Processor Service API",
    description="A simple FastAPI File Processor Service for processing files",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring service status"""
    return {
        "status": "healthy",
        "service": "file-processor-service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health/ready")
def health_check_ready():
    """Readiness check endpoint for Kubernetes/container orchestration"""
    return {
        "status": "ready",
        "service": "file-processor-service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
