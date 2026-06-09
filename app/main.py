"""Application entry point.

Run locally with:
    uv run fastapi dev app/main.py

Interactive API docs are then available at http://127.0.0.1:8000/docs
"""

import contextlib
import logging
from fastapi import FastAPI
from app.routers import health, messaging
from app.mcp import mcp

logging.basicConfig(level=logging.INFO)

# streamable_http_app() lazily creates the session manager, so it must be called
# before the lifespan runs (where we access mcp.session_manager).
_mcp_app = mcp.streamable_http_app()


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI):
    # FastAPI does not propagate lifespan events to mounted sub-applications, so
    # the session manager's run() context manager is never called automatically.
    # We call it here instead: it creates the anyio task group that the session
    # manager needs to handle concurrent MCP sessions for the server's lifetime.
    async with mcp.session_manager.run():
        yield


app = FastAPI(title="Test Service", version="0.1.0", lifespan=lifespan)

app.include_router(health.router)
app.include_router(messaging.router)
app.mount("/mcp", _mcp_app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
