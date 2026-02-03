# Rappel Conso Development

## Development Setup

```bash
# Create virtual environment
uv venv  # or: python -m venv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install all dependencies (runtime + development)
uv pip install -r requirements_dev.txt  # or: pip install -r requirements_dev.txt

# Install pre-commit hooks
pre-commit install

# Verify setup by running hooks on all files
pre-commit run --all-files
```

## Code Quality

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit:

```bash
# Install hooks (one time)
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run
```

### Linting and Formatting

```bash
# Ruff - Linting
ruff check custom_components/rappel_conso

# Ruff - Auto-fix issues
ruff check --fix custom_components/rappel_conso

# Ruff - Formatting
ruff format custom_components/rappel_conso

# MyPy - Type checking
mypy custom_components/rappel_conso

# PyLint - Additional linting
pylint custom_components/rappel_conso
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=custom_components.rappel_conso --cov-report=html

# Run specific test file
pytest tests/test_config_flow.py

# Run tests with verbose output
pytest -v
```

## Manual Testing

1. Copy the `custom_components/rappel_conso` directory to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Rappel Conso"

## Release Process

1. Update version in `manifest.json`
2. Update `CHANGELOG.md` with changes
3. Commit changes: `git commit -am "Release vX.Y.Z"`
4. Create tag: `git tag vX.Y.Z`
5. Push: `git push && git push --tags`
6. GitHub Actions will validate HACS compatibility

## Technical Decisions

### HTTP Client: httpx vs datagouv-client

**Decision:** Use `httpx.AsyncClient` directly instead of the official `datagouv-client` library.

**Rationale:**

1. **Simplicity**: The integration only needs read-only access to a single public dataset (RappelConso V2). The `datagouv-client` library is designed for full dataset management (create, update, delete operations) which is unnecessary overhead.

2. **Minimal Dependencies**: Using `httpx` directly keeps the dependency tree small, which is a best practice for Home Assistant custom integrations.

3. **Async-First**: The current `httpx.AsyncClient` implementation is already async/await compatible, perfect for Home Assistant's event loop.

4. **Full Control**: Direct API access provides complete control over request handling, pagination, error management, and timeout configuration without abstraction layers.

5. **No Rappel Conso-Specific Client**: There is no dedicated library for the Rappel Conso dataset specifically - `datagouv-client` is generic and would still require manual handling of the Rappel Conso data structure.

**Implementation:**
- HTTP client in `coordinator.py` lines 45-52
- API constants in `const.py`
- Pydantic models for validation in `models.py`

**Alternative Considered:**
- [datagouv-client](https://pypi.org/project/datagouv-client/) - Official Python wrapper for data.gouv.fr API
- Rejected due to unnecessary complexity for read-only operations on a single dataset

**Date:** 2026-01-30

## Project Structure

```
rappel-conso/
├── custom_components/rappel_conso/  # Integration code
├── tests/                            # Test suite
├── .github/workflows/                # CI/CD
└── docs/                             # Documentation
```
