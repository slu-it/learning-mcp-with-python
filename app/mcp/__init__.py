from mcp.server.fastmcp import FastMCP

mcp = FastMCP("example-server", streamable_http_path="/")

from app.mcp import contacts, messaging as _  # noqa: E402, F401
