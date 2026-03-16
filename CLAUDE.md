# FireFlayer

A Python app that cleans and transforms [Firefly III](https://www.firefly-iii.org/) transactions on import or in bulk.

## Stack

Python 3.10, Flask (webhook mode), pytest, ruff.

## Common commands

```bash
# Install dependencies
pip install -e .

# Run tests
pytest

# Lint
ruff check .
ruff format .

# Run pre-commit on all files
pre-commit run --all-files
```

## Architecture

- `fireflayer/fireflayer.py` — entrypoint, webhook and process modes
- `fireflayer/flayer.py` — core transaction transformation logic
- `fireflayer/firefly_client.py` — Firefly III API client
- `fireflayer/split_transaction.py` — split transaction handling
- `tests/` — pytest tests

## Conventions

- Commits must follow Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, etc. (enforced by commitizen)
- Merging to main triggers a GitHub release via semantic-release if commits warrant one
- Line length: 180 (ruff enforced)
- Target: Python 3.10
- Config via `fireflayer_config.yaml` with `flay` rules (name, function, arguments)
