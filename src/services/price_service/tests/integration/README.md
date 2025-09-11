# Price Service Integration Tests

This directory contains integration tests for the Price Service that test real PostgreSQL database interactions.

## Test Files

- `conftest.py` - Test configuration and fixtures for integration tests
- `test_database_schema.py` - Tests database schema and constraints
- `test_database_crud.py` - Tests CRUD operations with real database
- `test_database_performance.py` - Tests performance and scalability

## Prerequisites

- Docker installed and running
- PostgreSQL test container will be automatically managed by the tests

## Running Integration Tests

### Run all integration tests:
```bash
pytest tests/integration/ -v
```

### Run specific test files:
```bash
pytest tests/integration/test_database_schema.py -v
pytest tests/integration/test_database_crud.py -v
pytest tests/integration/test_database_performance.py -v
```

### Run with specific markers:
```bash
pytest tests/integration/ -m "not performance" -v  # Skip performance tests
pytest tests/integration/ -m "performance" -v       # Run only performance tests
```

## Test Environment

The integration tests use a dedicated PostgreSQL container:
- Container name: `products_watch_test_postgres`
- Port: `5433` (to avoid conflicts with main database)
- Database: `products_watch_test`
- User: `postgres`
- Password: `password`

## Test Categories

### Schema Tests
- Verify table structure and columns
- Check data types and constraints
- Validate indexes and relationships

### CRUD Tests
- Test all CRUD operations with real database
- Verify data integrity and validation
- Test error handling and edge cases

### Performance Tests
- Measure operation response times
- Test bulk operations
- Verify concurrent operation handling
- Test with large datasets

## Environment Variables

You can customize the test environment using these environment variables:

- `POSTGRES_TEST_HOST` - PostgreSQL host (default: localhost)
- `POSTGRES_TEST_PORT` - PostgreSQL port (default: 5433)
- `POSTGRES_TEST_USER` - PostgreSQL user (default: postgres)
- `POSTGRES_TEST_PASSWORD` - PostgreSQL password (default: password)
- `POSTGRES_TEST_DB` - PostgreSQL database (default: products_watch_test)

## Notes

- Tests automatically manage the PostgreSQL container lifecycle
- Each test function gets a fresh database session with transaction rollback
- Performance tests may take longer to complete
- Tests are designed to be run in isolation and clean up after themselves
