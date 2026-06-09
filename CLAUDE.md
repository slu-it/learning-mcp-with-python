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

## Authentication

`/health` is anonymous. Everything else requires a Keycloak-issued JWT (validated against the realm's JWKS: signature, issuer, audience) carrying the right scope:

- **`/mcp`** — an OAuth 2.0 protected resource enforced by the MCP SDK; requires the `mcp:tools` scope.
- **`/api/**`** — the plain REST routes; require the `test-service-api` scope, enforced by the `RequireScope` FastAPI dependency (`app/dependencies.py` wires the singleton `require_api_scope`, attached to each `/api` router).

- **`app/config.py`** — env-driven settings (`Settings` / `get_settings()`), read from environment variables or a `.env` file (see `.env.example`).
- **`app/auth.py`** — `JWTVerifier` validates JWTs against the realm's JWKS; `build_auth_settings()` produces the `AuthSettings` passed to `FastMCP`, and `RequireScope` is the reusable bearer-token dependency for the REST routes. The MCP SDK enforces its scope and serves RFC 9728 metadata.
- The MCP SDK's auth applies only to the HTTP transport. The stdio transport and in-process `mcp.call_tool()` (used by tests) are unauthenticated.
- Protected Resource Metadata is published at `/.well-known/oauth-protected-resource` (registered on the root app in `app/main.py`, since the MCP sub-app's own copy is unreachable under the `/mcp` mount).

## HTTP test files

`development/http/` contains `.http` files for manual endpoint testing (compatible with JetBrains HTTP client and VS Code REST Client).
