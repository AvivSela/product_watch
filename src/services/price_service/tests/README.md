# Price Service Tests

This directory contains comprehensive tests for the Price Service.

## Test Structure

- `conftest.py` - Test configuration and fixtures
- `test_health.py` - Health check endpoint tests
- `test_crud.py` - CRUD operation unit tests
- `integration/` - Integration tests with real PostgreSQL database

## Running Tests

### Run all tests:
```bash
pytest tests/ -v
```

### Run unit tests only:
```bash
pytest tests/test_*.py -v
```

### Run integration tests:
```bash
pytest tests/integration/ -v
```

### Run specific test files:
```bash
pytest tests/test_health.py -v
pytest tests/test_crud.py -v
```

## Test Categories

### Unit Tests
- Use SQLite in-memory database for fast execution
- Test individual components in isolation
- Verify API endpoints and data validation
- Test error handling and edge cases

### Integration Tests
- Use real PostgreSQL database
- Test complete workflows
- Verify database schema and constraints
- Performance and scalability testing

## Test Data

Tests use sample data fixtures defined in `conftest.py`:
- `sample_price_data` - Basic price data for testing
- `sample_price_data_2` - Alternative price data for testing

## Coverage

Tests cover:
- ✅ Health check endpoints
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Data validation and error handling
- ✅ Pagination functionality
- ✅ Database schema and constraints
- ✅ Performance and scalability
- ✅ Concurrent operations

## Prerequisites

- Python 3.11+
- pytest
- FastAPI test client
- SQLAlchemy
- PostgreSQL (for integration tests)
- Docker (for integration tests)
