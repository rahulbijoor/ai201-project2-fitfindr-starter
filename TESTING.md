# FitFindr Testing Guide

This project uses **pytest** for all testing. Pytest provides a standardized, professional testing framework for Python projects.

## Setup

### Install pytest (if not already installed)

```bash
pip install pytest
```

The project already includes pytest in `requirements.txt`.

## Running Tests

### Run all tests

```bash
pytest
```

This will:
- Discover all test files in the `tests/` directory
- Run all test functions
- Display a summary report

### Run with verbose output

```bash
pytest -v
```

Shows each test individually with [PASS] or [FAIL]

### Run specific test file

```bash
pytest tests/test_search_listings.py
```

### Run specific test class

```bash
pytest tests/test_search_listings.py::TestSearchListings
```

### Run specific test function

```bash
pytest tests/test_search_listings.py::TestSearchListings::test_search_returns_results
```

### Run tests matching a pattern

```bash
pytest -k "search"  # Runs all tests with "search" in the name
```

### Run with color output

```bash
pytest -v --color=yes
```

### Run in parallel (faster)

```bash
pip install pytest-xdist
pytest -n auto  # Uses all CPU cores
```

## Test Structure

### Files

- `tests/conftest.py` - Shared fixtures and configuration
- `tests/test_search_listings.py` - Tests for Tool 1
- `tests/test_suggest_outfit.py` - Tests for Tool 2
- `tests/test_create_fit_card.py` - Tests for Tool 3
- `tests/test_compare_price.py` - Tests for Tool 4
- `tests/test_trending_styles.py` - Tests for Tool 5
- `tests/test_integration.py` - End-to-end flow tests

### Fixtures

Fixtures are reusable test data/setup defined in `conftest.py`:

```python
@pytest.fixture
def listings():
    """Load all listings from the dataset."""
    return load_listings()

@pytest.fixture
def example_wardrobe():
    """Load the example wardrobe."""
    return get_example_wardrobe()
```

Use fixtures by passing them as parameters to test functions:

```python
def test_something(listings, example_wardrobe):
    # Use listings and example_wardrobe here
    pass
```

## Writing New Tests

### Basic test

```python
def test_my_feature():
    result = my_function("input")
    assert result == "expected"
```

### Test with fixture

```python
def test_with_data(listings):
    assert len(listings) > 0
```

### Test with parameters

```python
@pytest.mark.parametrize("input,expected", [
    ("a", 1),
    ("b", 2),
])
def test_multiple_inputs(input, expected):
    assert my_function(input) == expected
```

### Test for exceptions

```python
def test_raises_error():
    with pytest.raises(ValueError):
        bad_function()
```

## Common Assertions

```python
assert value == expected              # Equality
assert len(items) > 0                 # Length
assert "text" in my_string            # Substring
assert item in collection             # Membership
assert callable(my_function)          # Callable
assert isinstance(obj, MyClass)       # Type
```

## Test Coverage

### Generate coverage report

```bash
pip install pytest-cov
pytest --cov=. --cov-report=html
# Opens htmlcov/index.html
```

### Show coverage in terminal

```bash
pytest --cov=. --cov-report=term-missing
```

## Best Practices

1. **One assertion per test** (ideally) or related assertions in one test
2. **Clear test names** - describe what is being tested: `test_search_filters_by_price`
3. **Use fixtures** for common setup (data, configurations)
4. **Use parametrize** for testing multiple similar inputs
5. **Test both success and failure cases**
6. **Keep tests independent** - one test's failure shouldn't affect another

## Test Summary

Total tests available:

- **Tool 1 (search_listings)**: 7 unit tests + parametrized tests
- **Tool 2 (suggest_outfit)**: 8 tests
- **Tool 3 (create_fit_card)**: 11 tests + parametrized tests
- **Tool 4 (compare_price)**: 6 tests
- **Tool 5 (get_trending_styles)**: 10 tests + parametrized tests
- **Integration**: 5 complete flow tests

**Total: 40+ tests**

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pytest -v
```

## Troubleshooting

### Imports failing in tests?

Make sure you're running pytest from the project root:

```bash
cd /path/to/fitfindr
pytest
```

### Fixtures not found?

Check that `conftest.py` is in the `tests/` directory.

### Tests hanging on LLM calls?

Tests that call `suggest_outfit()` or `create_fit_card()` will call Groq API. Ensure `GROQ_API_KEY` is in `.env`.

### Want to skip API calls in tests?

Mock the LLM response (future enhancement):

```python
from unittest.mock import patch

@patch('tools._get_groq_client')
def test_outfit_mocked(mock_client):
    # Test without hitting real API
    pass
```
