# Learning: MCP with Python

This repository contains code I've written to implement an MCP server using Python.

## Repository Setup

After cloning, activate the git hooks:

```bash
git config core.hooksPath .githooks
```

This enables a pre-commit hook that runs formatting checks, linting, and type checking before each commit.

## Local Setup

The MCP server is secured using OAuth2.
The setup for that is based on https://modelcontextprotocol.io/docs/tutorials/security/authorization#keycloak-setup.

Keycloak can be started using Docker Compose with [docker-compose.yml](docker-compose.yml):

* defines a volume to keep data between sessions
* server is available under localhost:8080

### First Time Setup

When starting Keycloak for the first time, the steps from the original documentation need to be applied:

* create client scope `mcp:tools` with type "Default" and enabled inclusion in token scope
* configure audience mapper for that scope with custom audience = `http://localhost:8000` (must match `MCP_SERVER_URL`)
* configure client registration by disabling "client URIs must match" and add you local IP to the trusted hosts

Additionally, since the `/api/**` endpoints are also protected, you might want to create a custom OAuth2 client and scope:

* Client Scope:
  * create client scope `test-service-api` with type "Default" and enabled inclusion in token scope
  * configure audience mapper for that scope with custom audience = `http://localhost:8000` (must match `MCP_SERVER_URL`)
* Client:
  * "Client Authentication": true
  * "Authorization": true
  * "Direct Access Grandts": true
  * add `test-service-api` scope as default

## Testing with HTTP Client

Under `development/http` you'll find example HTTP requests (IntelliJ Client) for interacting with the API and MCP endpoints.
You just need to create a `http-client.private.env.json` file containing the `clientId` and `clientSecret` values.

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

When starting Claude afterward, the MCP server will be in the "needs authentication" state (check with the`/mcp` command).
Starting the authentication process should open a browser window where Keycloak asks you to approve the registration.
After that the MCP server should be usable.
