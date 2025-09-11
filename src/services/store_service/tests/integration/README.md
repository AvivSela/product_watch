# Store Service Integration Tests

This directory contains integration tests for the Store Service that test real PostgreSQL database interactions.

## Overview

Integration tests verify that the service works correctly with a real PostgreSQL database, testing:
- Database schema and constraints
- CRUD operations with real persistence
- Database performance characteristics
- Transaction handling
- Connection management

## Test Structure

```
integration/
├── conftest.py                    # Test fixtures and PostgreSQL setup
├── test_database_crud.py         # CRUD operations with real database
├── test_database_performance.py  # Performance and scalability tests
├── test_database_schema.py       # Database schema validation tests
└── README.md                     # This file
```

## Prerequisites

- Docker and Docker Compose installed
- Python 3.8+ with pytest
- PostgreSQL client tools (optional, for debugging)

## Running Integration Tests

### Option 1: Using the Test Runner (Recommended)

```bash
# Run only integration tests
python run_all_tests.py --type integration

# Run all tests (unit + integration)
python run_all_tests.py --type all
```

### Option 2: Using Docker Compose

```bash
# Start PostgreSQL test container
docker-compose -f docker-compose.test.yml up -d postgres-test

# Run integration tests
python scripts/run_integration_tests.py

# Clean up
docker-compose -f docker-compose.test.yml down -v
```

### Option 3: Manual Setup

```bash
# Start PostgreSQL container manually
docker run -d --name products_watch_test_postgres \
  -p 5433:5432 \
  -e POSTGRES_DB=products_watch_test \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  postgres:15-alpine

# Wait for PostgreSQL to be ready
docker exec products_watch_test_postgres pg_isready -U postgres

# Run tests locally
python scripts/run_integration_tests.py local

# Clean up
docker rm -f products_watch_test_postgres
```

## Environment Variables

The integration tests use the following environment variables:

```bash
POSTGRES_TEST_HOST=localhost          # PostgreSQL host
POSTGRES_TEST_PORT=5433               # PostgreSQL port (different from main)
POSTGRES_TEST_USER=postgres           # PostgreSQL user
POSTGRES_TEST_PASSWORD=password       # PostgreSQL password
POSTGRES_TEST_DB=products_watch_test  # Test database name
```

## Test Categories

### 1. Database CRUD Integration (`test_database_crud.py`)

Tests real database persistence:
- Store creation with database verification
- Constraint enforcement
- Transaction rollback behavior
- Update and delete operations
- Pagination with real data

### 2. Database Performance (`test_database_performance.py`)

Tests performance characteristics:
- Bulk insert performance
- Query performance with indexes
- Pagination performance
- Connection pool performance
- Transaction performance
- Memory usage with large datasets

### 3. Database Schema (`test_database_schema.py`)

Tests database schema:
- Table and column existence
- Data type validation
- Constraint validation
- Index verification
- Migration compatibility

## Test Fixtures

### Session-scoped Fixtures
- `postgres_manager`: Manages PostgreSQL container lifecycle
- `integration_engine`: Database engine for the test session

### Function-scoped Fixtures
- `integration_db_session`: Database session with transaction rollback
- `integration_client`: FastAPI test client with real database
- `sample_store_data`: Test data for single store operations
- `multiple_stores_data`: Test data for bulk operations

## Key Features

### Transaction Isolation
Each test runs in its own transaction that is rolled back after the test, ensuring:
- Tests don't interfere with each other
- No test data pollution
- Consistent test environment

### Real Database Testing
- Uses actual PostgreSQL (not SQLite)
- Tests real database constraints
- Validates actual SQL performance
- Tests connection handling

### Performance Testing
- Measures actual query performance
- Tests bulk operations
- Validates index usage
- Monitors memory usage

## Troubleshooting

### PostgreSQL Container Issues

```bash
# Check container status
docker ps -a | grep products_watch_test_postgres

# View container logs
docker logs products_watch_test_postgres

# Restart container
docker restart products_watch_test_postgres
```

### Connection Issues

```bash
# Test PostgreSQL connection
docker exec products_watch_test_postgres psql -U postgres -d products_watch_test -c "SELECT version();"

# Check if port is available
netstat -an | grep 5433
```

### Test Failures

1. **Container not starting**: Check Docker daemon is running
2. **Connection refused**: Wait for PostgreSQL to be ready (30s startup time)
3. **Permission denied**: Check Docker permissions
4. **Port conflicts**: Change `POSTGRES_TEST_PORT` environment variable

## Best Practices

1. **Keep tests isolated**: Each test should be independent
2. **Use realistic data**: Test with data similar to production
3. **Test edge cases**: Include boundary conditions and error scenarios
4. **Monitor performance**: Set reasonable performance expectations
5. **Clean up**: Always clean up containers after tests

## Integration with CI/CD

The integration tests are designed to work in CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run Integration Tests
  run: |
    python run_all_tests.py --type integration
  env:
    POSTGRES_TEST_HOST: localhost
    POSTGRES_TEST_PORT: 5433
```

## Performance Expectations

Typical performance benchmarks:
- Single store creation: < 100ms
- Bulk insert (100 stores): < 10s
- Pagination query: < 100ms
- Indexed lookup: < 10ms
- Large result set (1000 records): < 1s

Adjust these expectations based on your hardware and requirements.
