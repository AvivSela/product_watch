# Retail File Service Integration Tests

This directory contains integration tests for the Retail File Service that test real PostgreSQL database interactions.

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
python scripts/run_integration_tests.py retail

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
python scripts/run_integration_tests.py local retail

# Clean up
docker rm -f products_watch_test_postgres
```

## Test Categories

### Schema Tests
- Verify table structure and columns
- Check data types and constraints
- Validate indexes and relationships
- Test unique constraints on (chain_id, store_id, file_name)

### CRUD Tests
- Test all CRUD operations with real database
- Verify data integrity and validation
- Test error handling and edge cases
- Test unique constraint enforcement
- Test nullable field handling

### Performance Tests
- Measure operation response times
- Test bulk operations
- Verify concurrent operation handling
- Test with large datasets
- Test pagination performance
- Test query performance with indexes

### Kafka Integration Tests
- Test Kafka message production when creating retail files
- Verify message structure and content
- Test error handling scenarios
- Test JSON serialization compatibility
- Test message size constraints
- Test integration with multiple files

## Test Data

Tests use sample data fixtures defined in `conftest.py`:
- `sample_retail_file_data` - Basic retail file data for testing
- `sample_retail_file_data_2` - Alternative retail file data for testing
- `multiple_retail_files_data` - Multiple retail files for bulk testing

## Environment Variables

You can customize the test environment using these environment variables:

- `POSTGRES_TEST_HOST` - PostgreSQL host (default: localhost)
- `POSTGRES_TEST_PORT` - PostgreSQL port (default: 5433)
- `POSTGRES_TEST_USER` - PostgreSQL user (default: postgres)
- `POSTGRES_TEST_PASSWORD` - PostgreSQL password (default: password)
- `POSTGRES_TEST_DB` - PostgreSQL database (default: products_watch_test)

## Coverage

Tests cover:
- ✅ Health check endpoints
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Data validation and error handling
- ✅ Pagination functionality
- ✅ Database schema and constraints
- ✅ Unique constraint on (chain_id, store_id, file_name)
- ✅ Performance and scalability
- ✅ Concurrent operations
- ✅ Transaction handling
- ✅ Connection management
- ✅ Kafka message production
- ✅ Kafka message structure and content
- ✅ Kafka error handling
- ✅ JSON serialization compatibility

## Database Schema

The integration tests verify the following database schema:

### Table: retail_files
- `id` (UUID, Primary Key)
- `chain_id` (VARCHAR, Not Null)
- `store_id` (INTEGER, Nullable)
- `file_name` (VARCHAR, Not Null)
- `file_path` (VARCHAR, Not Null)
- `file_size` (INTEGER, Nullable)
- `upload_date` (TIMESTAMP, Not Null)
- `is_processed` (BOOLEAN, Not Null)
- `created_at` (TIMESTAMP, Not Null)
- `updated_at` (TIMESTAMP, Not Null)

### Constraints
- Unique constraint on (chain_id, store_id, file_name)
- Primary key on id
- Not null constraints on required fields

## Performance Benchmarks

The performance tests include benchmarks for:
- Bulk insert operations (100 records in < 10s)
- Indexed queries (< 0.1s)
- Pagination (5 pages in < 2s)
- Connection pool operations (20 operations in < 5s)
- Transaction operations (30 operations in < 8s)
- Large result set queries (< 1s)
- Concurrent reads (50 operations in < 2s)

## Troubleshooting

### Common Issues

1. **PostgreSQL container not starting**
   - Ensure Docker is running
   - Check if port 5433 is available
   - Verify Docker has sufficient resources

2. **Connection timeout**
   - Wait longer for PostgreSQL to be ready
   - Check container logs: `docker logs products_watch_test_postgres`

3. **Test failures**
   - Ensure all dependencies are installed
   - Check database connection settings
   - Verify test data fixtures are correct

### Debug Mode

To enable SQL debugging, set `echo=True` in the `integration_engine` fixture in `conftest.py`.

### Manual Database Inspection

```bash
# Connect to test database
docker exec -it products_watch_test_postgres psql -U postgres -d products_watch_test

# List tables
\dt

# Describe retail_files table
\d retail_files

# Check constraints
SELECT conname, contype FROM pg_constraint WHERE conrelid = 'retail_files'::regclass;
```
