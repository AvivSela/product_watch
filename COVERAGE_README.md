# Test Coverage Guide

This guide explains how to run tests with coverage reporting for both unit and integration tests.

## Overview

The project now supports comprehensive test coverage reporting that combines both unit and integration test results. This gives you a complete picture of your code coverage across all test types.

## Installation

The required coverage package is already installed:
```bash
pip install pytest-cov==4.1.0
```

## Running Tests with Coverage

### 1. Combined Coverage (Recommended)

Run both unit and integration tests with combined coverage reporting:

```bash
python scripts/run_coverage_tests.py
```

This will:
- Run unit tests for all services with coverage
- Run integration tests for all services with coverage
- Combine all coverage data
- Generate comprehensive reports

### 2. Unit Tests Only

```bash
python scripts/run_coverage_tests.py --unit-only
```

### 3. Integration Tests Only

```bash
python scripts/run_coverage_tests.py --integration-only
```

### 4. Specific Service

```bash
python scripts/run_coverage_tests.py --service retail
```

Available services: `product`, `store`, `price`, `retail`

## Coverage Reports Generated

### Individual Service Reports

Each service generates its own coverage reports in the service directory:
- **Terminal output**: Shows coverage percentage and missing lines
- **HTML report**: `htmlcov/index.html` - Interactive web report
- **XML report**: `coverage.xml` - For CI/CD integration
- **JSON report**: `coverage.json` - Machine-readable format

### Combined Reports (Project Root)

When running the full coverage script:
- **Combined HTML**: `combined_htmlcov/index.html` - All services combined
- **Combined XML**: `combined_coverage.xml` - For CI/CD integration

## Coverage Configuration

Each service's `pytest.ini` includes coverage options:

```ini
addopts = -v --tb=short -m "not integration" --cov=. --cov-report=term-missing --cov-report=html:htmlcov --cov-report=xml:coverage.xml
```

## Manual Coverage Commands

### Run Unit Tests with Coverage (Single Service)

```bash
cd src/services/retail_file_service
pytest tests -m unit --cov=. --cov-report=term-missing --cov-report=html:htmlcov
```

### Run Integration Tests with Coverage (Single Service)

```bash
cd src/services/retail_file_service
pytest tests/integration -m integration --cov=. --cov-report=term-missing --cov-report=html:htmlcov
```

### Combine Multiple Coverage Files

```bash
coverage combine .coverage*
coverage report --show-missing
coverage html
```

## Understanding Coverage Reports

### Terminal Output
```
Name                 Stmts   Miss  Cover   Missing
--------------------------------------------------
main.py                 45      2    96%   23, 45
models.py               30      0   100%
database.py             25      3    88%   12-14
--------------------------------------------------
TOTAL                  100      5    95%
```

### HTML Report Features
- **Line-by-line coverage**: See exactly which lines are covered
- **Branch coverage**: Shows conditional logic coverage
- **Missing lines**: Highlighted in red
- **Covered lines**: Highlighted in green
- **Interactive navigation**: Click through files and functions

## Best Practices

1. **Aim for high coverage**: Target 80%+ overall coverage
2. **Focus on critical paths**: Ensure business logic is well covered
3. **Review missing lines**: Pay attention to uncovered code
4. **Regular monitoring**: Run coverage reports regularly during development
5. **CI/CD integration**: Use XML reports in your CI pipeline

## Troubleshooting

### Coverage Files Not Found
- Ensure pytest-cov is installed: `pip install pytest-cov`
- Check that tests are running successfully first
- Verify pytest.ini configuration

### Integration Tests Failing
- Ensure PostgreSQL test container is running
- Check environment variables are set correctly
- Verify Docker Compose setup

### Low Coverage
- Add more test cases for uncovered functions
- Review test quality, not just quantity
- Consider edge cases and error conditions

## Example Workflow

1. **Development**: Write code and unit tests
2. **Unit Coverage**: Run `python scripts/run_coverage_tests.py --unit-only`
3. **Integration**: Add integration tests
4. **Full Coverage**: Run `python scripts/run_coverage_tests.py`
5. **Review**: Open `combined_htmlcov/index.html` in browser
6. **Improve**: Add tests for uncovered code
7. **Repeat**: Continue until coverage goals are met

## Integration with CI/CD

The XML reports can be integrated with CI/CD systems:

```yaml
# Example GitHub Actions step
- name: Run tests with coverage
  run: python scripts/run_coverage_tests.py

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./combined_coverage.xml
```

This setup provides comprehensive test coverage visibility across your entire microservices architecture.
