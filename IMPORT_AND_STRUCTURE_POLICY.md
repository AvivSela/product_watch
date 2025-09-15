# Import and Project Structure Policy

## Overview

This policy defines the standards for Python imports and project structure for the Products Watch microservices system. The policy ensures compatibility with unit testing, integration testing, command-line execution, and Docker deployment.

## Project Structure

### Root Structure
```
products_watch_4/
├── src/                          # Source code root
│   ├── __init__.py              # Package marker
│   ├── services/                # Microservices
│   │   ├── service_name/        # Individual service
│   │   │   ├── __init__.py      # Service package marker
│   │   │   ├── main.py          # Service entry point
│   │   │   ├── models.py        # Pydantic models
│   │   │   ├── database.py      # Database schemas & connections
│   │   │   ├── Dockerfile       # Service-specific Docker config
│   │   │   ├── requirements.txt # Service-specific dependencies
│   │   │   └── tests/           # Service tests
│   │   │       ├── __init__.py
│   │   │       ├── conftest.py  # Test configuration
│   │   │       ├── test_*.py    # Unit tests
│   │   │       └── integration/ # Integration tests
│   │   │           ├── __init__.py
│   │   │           ├── conftest.py
│   │   │           └── test_*.py
│   │   └── ...
│   └── shared/                  # Shared utilities
│       ├── __init__.py
│       └── utils/               # Common utilities
│           ├── __init__.py
│           ├── kafka_consumer.py
│           ├── kafka_producer.py
│           └── ...
├── scripts/                     # Utility scripts
├── docker-compose.yml          # Development environment
├── docker-compose.testing.yml  # Testing environment
├── setup.py                    # Package configuration
├── requirements.txt            # Global dependencies
└── pytest.ini                 # Global test configuration
```

## Import Policy

### 1. Import Order and Organization

All Python files MUST follow this import order:

```python
# 1. Standard library imports
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# 2. Third-party imports
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

# 3. Local application imports
from .database import get_db
from .models import Price, PriceCreate
from ..shared.utils.kafka_consumer import KafkaConsumer
```

### 2. Import Strategies by Context

#### A. Service Internal Imports (Within Same Service)
Use **relative imports** for modules within the same service:

```python
# ✅ CORRECT - Relative imports within service
from .database import get_db
from .models import Price, PriceCreate
from .file_processor import process_xml_file

# ❌ INCORRECT - Absolute imports within service
from services.price_service.database import get_db
```

#### B. Cross-Service Imports (Between Different Services)
Use **absolute imports** with full package path:

```python
# ✅ CORRECT - Absolute imports for cross-service
from shared.utils.kafka_consumer import KafkaConsumer
from shared.utils.kafka_producer import KafkaProducer

# ❌ INCORRECT - Relative imports across services
from ...shared.utils.kafka_consumer import KafkaConsumer
```

#### C. Shared Utilities Imports
Always use **absolute imports** for shared utilities:

```python
# ✅ CORRECT - Absolute imports for shared utilities
from shared.utils.kafka_consumer import KafkaConsumer
from shared.utils.kafka_producer import KafkaProducer

# ❌ INCORRECT - Relative imports for shared utilities
from ...shared.utils.kafka_consumer import KafkaConsumer
```

### 3. Test Environment Handling

#### A. Test Detection
Use environment variables to detect test context:

```python
import os

# Detect test environment
IS_TESTING = os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TESTING")
```

#### B. Conditional Imports for Tests
Implement fallback import strategies in service `__init__.py` files:

```python
# services/service_name/__init__.py
import os
import sys

# Add service directory to Python path for testing
service_dir = os.path.dirname(__file__)
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

try:
    # Try relative imports first (production)
    from .models import Price, PriceCreate
    from .database import get_db
except ImportError:
    # Fallback to absolute imports (testing)
    try:
        from models import Price, PriceCreate
        from database import get_db
    except ImportError:
        # Final fallback - set to None for optional imports
        Price = None
        PriceCreate = None
        get_db = None

__all__ = ["Price", "PriceCreate", "get_db"]
```

#### C. Main Module Import Strategy
Use conditional imports in `main.py` files:

```python
# services/service_name/main.py
import os

if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TESTING"):
    # Test environment - use absolute imports
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
    from shared.utils.kafka_consumer import KafkaConsumer
    from .models import Price, PriceCreate
else:
    # Production environment - use relative imports
    from ...shared.utils.kafka_consumer import KafkaConsumer
    from .models import Price, PriceCreate
```

### 4. Test Configuration

#### A. Test conftest.py Setup
Each service's `tests/conftest.py` MUST:

```python
# tests/conftest.py
import os
import sys

# Set testing environment variable
os.environ["TESTING"] = "true"

# Add necessary paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", ".."))

# Import service components
from main import app
from database import Base, get_db
```

#### B. Integration Test Setup
Integration tests MUST use absolute imports:

```python
# tests/integration/test_database.py
import pytest
from services.price_service.database import Base, get_db
from services.price_service.models import Price, PriceCreate
```

## Docker Configuration

### 1. Dockerfile Standards

Each service Dockerfile MUST:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code maintaining package structure
COPY src/ ./src/

# Set PYTHONPATH to include src directory
ENV PYTHONPATH=/app/src

# Expose service port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run service as module
CMD ["python", "-m", "services.service_name.main"]
```

### 2. Docker Compose Configuration

Services MUST be configured to use module execution:

```yaml
# docker-compose.yml
services:
  price-service:
    build:
      context: .
      dockerfile: src/services/price_service/Dockerfile
    environment:
      - PYTHONPATH=/app/src
    ports:
      - "8002:8002"
    command: ["python", "-m", "services.price_service.main"]
```

## Command Line Execution

### 1. Service Execution

Services MUST be executable from command line:

```bash
# From project root
python -m services.price_service.main

# From service directory
cd src/services/price_service
python main.py
```

### 2. Test Execution

Tests MUST be executable from multiple contexts:

```bash
# From project root - run all tests
pytest

# From project root - run specific service tests
pytest src/services/price_service/tests/

# From service directory
cd src/services/price_service
pytest tests/

# Run integration tests only
pytest src/services/price_service/tests/integration/
```

## Package Configuration

### 1. setup.py Configuration

The `setup.py` MUST be configured for proper package discovery:

```python
from setuptools import find_packages, setup

setup(
    name="products-watch",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    # ... other configuration
)
```

### 2. PYTHONPATH Configuration

The project MUST work with `PYTHONPATH=/app/src` in Docker and `PYTHONPATH=src` in development.

## Validation Rules

### 1. Import Validation

- ✅ All imports MUST follow the specified order
- ✅ Relative imports MUST be used within the same service
- ✅ Absolute imports MUST be used for shared utilities
- ✅ Test environment detection MUST be implemented
- ✅ Fallback import strategies MUST be provided

### 2. Structure Validation

- ✅ Each service MUST have its own directory under `src/services/`
- ✅ Each service MUST have `__init__.py`, `main.py`, `models.py`, `database.py`
- ✅ Each service MUST have a `tests/` directory with `conftest.py`
- ✅ Shared utilities MUST be in `src/shared/utils/`
- ✅ Each service MUST have its own `Dockerfile`

### 3. Execution Validation

- ✅ Services MUST be executable via `python -m services.service_name.main`
- ✅ Services MUST be executable via `python main.py` from service directory
- ✅ Tests MUST be executable from project root and service directory
- ✅ Docker containers MUST start successfully
- ✅ Health checks MUST pass in Docker environment

## Migration Guide

### Converting Existing Services

1. **Update `__init__.py` files** with fallback import strategy
2. **Update `main.py` files** with conditional imports
3. **Update `conftest.py` files** with proper path setup
4. **Update Dockerfiles** to use module execution
5. **Update docker-compose.yml** to use module commands
6. **Test all execution contexts** (CLI, Docker, tests)

### Common Issues and Solutions

#### Issue: ImportError in tests
**Solution**: Add proper path setup in `conftest.py` and use `TESTING` environment variable

#### Issue: Module not found in Docker
**Solution**: Ensure `PYTHONPATH=/app/src` and use module execution (`python -m`)

#### Issue: Relative import errors
**Solution**: Use conditional imports based on execution context

## Examples

### Complete Service Example

See `src/services/price_service/` for a complete implementation following this policy.

### Test Example

```python
# tests/test_crud.py
import pytest
from fastapi.testclient import TestClient

from main import app

def test_create_price(client: TestClient):
    """Test price creation endpoint."""
    response = client.post("/prices", json={
        "chain_id": "test_chain",
        "store_id": 1,
        "item_code": "TEST_001",
        "price_amount": 9.99,
        "currency_code": "USD"
    })
    assert response.status_code == 201
```

This policy ensures consistent, maintainable, and testable code across all services while supporting multiple execution contexts.
