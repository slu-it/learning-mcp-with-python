from functools import lru_cache

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Public base URL of this server. Doubles as the OAuth 2.0 resource
    # identifier and the expected token `aud` (audience) claim.
    mcp_server_url: AnyHttpUrl = AnyHttpUrl("http://localhost:8000")

    # Scope a bearer token must carry to reach the MCP endpoint.
    mcp_required_scope: str = "mcp:tools"

    # Scope a bearer token must carry to reach the REST API (`/api/**`).
    api_required_scope: str = "api:access"

    # Keycloak (OAuth 2.0 authorization server) location.
    auth_host: str = "localhost"
    auth_port: int = 9000
    auth_realm: str = "master"

    audience: str = "learning-mcp-with-python"

    @property
    def issuer_url(self) -> str:
        """Token issuer (`iss`), e.g. ``http://localhost:9000/realms/master``."""
        return f"http://{self.auth_host}:{self.auth_port}/realms/{self.auth_realm}"

    @property
    def jwks_uri(self) -> str:
        """JWKS endpoint used to fetch the realm's token-signing keys."""
        return f"{self.issuer_url}/protocol/openid-connect/certs"


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings, instantiated once on first use."""
    return Settings()
