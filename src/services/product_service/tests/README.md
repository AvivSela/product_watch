# Product Service Tests

This directory contains comprehensive unit tests for the Product Service API.

## Test Structure

- `conftest.py` - Pytest configuration and fixtures
- `test_crud.py` - CRUD operation tests
- `test_health.py` - Health check endpoint tests

## Test Coverage

The tests cover:

### CRUD Operations
- ✅ Product creation (success and validation errors)
- ✅ Product retrieval (success and not found)
- ✅ Product listing with pagination
- ✅ Product updates (success, not found, constraint violations)
- ✅ Product deletion (success and not found)
- ✅ Duplicate constraint handling
- ✅ Cross-store product handling
- ✅ Complete CRUD workflow

### Health Checks
- ✅ Basic health check endpoint
- ✅ Database health check endpoint
- ✅ Health checks with existing data

### Validation
- ✅ Required field validation
- ✅ Data type validation
- ✅ Constraint validation (negative values, etc.)
- ✅ Unique constraint validation

## Test Database

Tests use an in-memory SQLite database for fast execution and isolation. Each test gets a fresh database session and tables are created/dropped automatically.

## Fixtures

- `client` - FastAPI test client with database override
- `db_session` - Fresh database session for each test
- `sample_product_data` - Sample product data for testing
- `sample_product_data_2` - Second sample product data for testing

## Test Data

The tests use realistic product data including:
- Chain IDs and Store IDs
- Item codes and names
- Manufacturer information
- Quantity and packaging details
- Various countries and units
