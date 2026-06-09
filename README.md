# Learning: MCP with Python

This repository contains code I've written to implement an MCP server using Python.

## Setup

After cloning, activate the git hooks:

```bash
git config core.hooksPath .githooks
```

This enables a pre-commit hook that runs formatting checks, linting, and type checking before each commit.

## Testing with Claude Code

To test if the MCP servers work using Claude Code, you can register them like this and afterward ask Claude "What is John's phone number?".

### STDIO

```
claude mcp add learning-mcp-with-python-stdio -- uv --directory /home/user/projects/learning-mcp-with-python run python -m app.mcp_stdio
```

### HTTP

```
# when using the full service (main.py)
claude mcp add --transport http learning-mcp-with-python-http http://localhost:8000/mcp

# when using just the MCP server (mcp_http.py)
claude mcp add --transport http learning-mcp-with-python-http http://localhost:8000/
```
