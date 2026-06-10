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
* server is available under localhost:9000

### First Time Setup

There are several different resources to configure to set up Keycloak.
To make things easy, there is a setup script in the form of a [HTTP client](development/keycloak-setup/initial-setup.http).
After starting Keycloak for the first time using Docker Compose, you can execute this client script ("run all") using the `dev` environment.

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
claude mcp add --transport http learning-mcp-with-python-http http://localhost:8000/mcp
```

When starting Claude afterward, the MCP server will be in the "needs authentication" state (check with the`/mcp` command).
Starting the authentication process should open a browser window where Keycloak asks you to approve the registration.
After that the MCP server should be usable.
