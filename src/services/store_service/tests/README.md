# Store Service Tests

This directory contains comprehensive unit tests for the Store Service API.

## Test Structure

- `conftest.py` - Pytest configuration and fixtures
- `test_crud.py` - CRUD operations tests
- `test_health.py` - Health check endpoint tests

## Running Tests

### From Store Service Directory
```bash
cd src/services/store_service
python -m pytest tests/ -v
```

### Using Test Runner Script
```bash
cd src/services/store_service
python run_tests.py
```

### From Project Root
```bash
python run_store_tests.py
```

## Test Coverage

### CRUD Operations
- ✅ Store creation (success, validation, duplicates)
- ✅ Store retrieval (single, pagination, not found)
- ✅ Store updates (success, validation, duplicates)
- ✅ Store deletion (success, not found)
- ✅ Complete CRUD workflow

### Health Checks
- ✅ Basic health check endpoint
- ✅ Database health check endpoint
- ✅ Database health check with data

### Validation Tests
- ✅ Required field validation
- ✅ Store code validation (positive integers only)
- ✅ Duplicate constraint validation (store_code + chain_id)

## Test Database

Tests use an in-memory SQLite database for isolation and speed. Each test gets a fresh database session that is cleaned up after the test completes.

## Fixtures

- `client` - FastAPI test client with database override
- `db_session` - Fresh database session for each test
- `sample_store_data` - Sample store data for testing
- `sample_store_data_2` - Second sample store data for testing
