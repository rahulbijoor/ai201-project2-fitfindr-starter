# FitFindr Test Suite

Comprehensive test coverage for all planning loop features and stretch features.

## Test Files

### Core Agent Tests
- **test_handle_query.py** — Tests Gradio UI handler (4 scenarios)
  - Happy path with example wardrobe
  - No results path  
  - Empty wardrobe path
  - Empty query guard

- **test_state_flow.py** — Verifies state passing through planning loop
  - Happy path: all state accumulates correctly
  - No results: downstream calls skipped
  - Empty wardrobe: downstream calls skipped

### Stretch Feature Tests
- **run_stretch_tests.py** — Comprehensive test runner for all stretch features
  - Price Comparison Tool (+2 pts)
  - Trend Awareness Tool (+2 pts)
  - Retry Logic with Fallback (+1 pt)
  - Integration tests

- **test_style_profile_memory.py** — Two-interaction profile memory demo
  - First interaction: Extract and save style preferences
  - Second interaction: Load and apply remembered preferences
  - Verify results match remembered style

- **test_stretch_features.py** — Pytest format for stretch features (if using pytest)

### Tool Tests (Original Pytest Suite)
- **test_search_listings.py** — search_listings() function tests
- **test_suggest_outfit.py** — suggest_outfit() function tests
- **test_create_fit_card.py** — create_fit_card() function tests
- **test_compare_price.py** — compare_price() function tests
- **test_trending_styles.py** — get_trending_styles() function tests
- **test_integration.py** — Integration tests for all tools

## Running Tests

### All Tests
```bash
# Run all Pytest tests
pytest tests/

# Run standalone test runners (no pytest required)
python tests/run_stretch_tests.py
python tests/test_state_flow.py
python tests/test_handle_query.py
python tests/test_style_profile_memory.py
```

### Specific Test Categories
```bash
# Core planning loop tests
pytest tests/test_handle_query.py tests/test_state_flow.py

# Stretch features only
python tests/run_stretch_tests.py
python tests/test_style_profile_memory.py

# Individual tools
pytest tests/test_search_listings.py
pytest tests/test_suggest_outfit.py
pytest tests/test_create_fit_card.py
```

## Test Coverage

| Component | Tests | Status |
|-----------|-------|--------|
| handle_query() | 4 scenarios | ✅ |
| State flow | 3 paths | ✅ |
| search_listings() | Multiple | ✅ |
| suggest_outfit() | Multiple | ✅ |
| create_fit_card() | Multiple | ✅ |
| compare_price() | Multiple | ✅ |
| get_trending_styles() | Multiple | ✅ |
| Price comparison | 3 tests | ✅ |
| Trend awareness | 2 tests | ✅ |
| Retry logic | 2 tests | ✅ |
| Style profile memory | 2 interactions | ✅ |
| **TOTAL** | **25+ tests** | **✅** |

## Test Approach

### Standalone Tests (No Dependencies)
Files that can run with just `python`:
- `test_handle_query.py` — Pure assertions, imports only app/agent
- `test_state_flow.py` — Pure assertions, imports only agent
- `run_stretch_tests.py` — Pure assertions, imports tools
- `test_style_profile_memory.py` — Pure assertions, imports style_profiles

### Pytest Tests (With Pytest)
Files that use pytest framework (existing tests):
- `conftest.py` — Pytest configuration and fixtures
- `test_*.py` (original files) — Pytest-format tests for individual tools
- `test_integration.py` — Integration tests

## Continuous Integration

All tests pass locally. Tests can be integrated into CI/CD pipelines:

```bash
# Quick check (core + stretch features)
python tests/run_stretch_tests.py && \
python tests/test_state_flow.py && \
python tests/test_handle_query.py && \
python tests/test_style_profile_memory.py

# Full check (all tests)
pytest tests/ -v
```

## Key Test Scenarios

### Happy Path (Required Features)
- Query parsing ✓
- Search returns results ✓
- Outfit suggestion generated ✓
- Fit card generated ✓
- Price analysis computed ✓

### Error Paths (Branching Logic)
- No results: error set, downstream skipped ✓
- Empty wardrobe: error set, outfit/fit_card skipped ✓
- Empty query: guard prevents execution ✓

### Stretch Features
- Price comparison: fair price analysis ✓
- Trend awareness: trending styles on empty search ✓
- Retry logic: automatic constraint loosening ✓
- Profile memory: saves and reuses preferences ✓

## Notes

- All standalone tests pass without external dependencies
- Pytest tests provide additional coverage and formalize test structure
- Test files are self-documenting with clear assertions
- Coverage includes happy paths, error paths, and edge cases
