from mcp.server.fastmcp import FastMCP

from app.auth import JWTVerifier, build_auth_settings
from app.config import get_settings

_settings = get_settings()

# Configuring `token_verifier` + `auth` makes the streamable-HTTP transport
# require a valid bearer token with the `mcp:tools` scope on the MCP endpoint.
# The stdio transport ignores these settings, and in-process `mcp.call_tool()`
# calls (used by the tests) bypass the HTTP auth layer entirely.
mcp = FastMCP(
    "example-server",
    token_verifier=JWTVerifier(_settings),
    auth=build_auth_settings(_settings),
)

from app.mcp import contacts, messaging as _  # noqa: E402, F401
