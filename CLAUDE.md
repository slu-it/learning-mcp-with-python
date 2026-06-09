# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands use `uv` as the package manager.

```bash
# Run dev server (hot reload, auto-docs at http://127.0.0.1:8000/docs)
uv run fastapi dev app/main.py

# Lint
uv run ruff check .

# Format
uv run ruff format .

# Type check
uv run mypy .

# Run tests
uv run pytest

# Run a single test
uv run pytest path/to/test_file.py::test_function_name
```

## Architecture

This is a FastAPI service structured in three layers:

- **`app/routers/`** — HTTP layer. Validates requests (FastAPI/Pydantic handle 422 automatically), delegates to services, maps `MessagingError` → 502.
- **`app/services/`** — Business logic. Dispatches to channel-specific handlers. Raises `MessagingError` on provider failures.
- **`app/schemas/`** — Pydantic models shared between layers. The `Channel` enum controls which channels are valid; adding a new member here automatically updates API validation.

## HTTP test files

`development/http/` contains `.http` files for manual endpoint testing (compatible with JetBrains HTTP client and VS Code REST Client).
