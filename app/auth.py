import logging

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from pydantic import AnyHttpUrl

from app.config import Settings, get_settings

_logger = logging.getLogger(__name__)
_settings = get_settings()


class JWTVerifier(TokenVerifier):
    """Verify JWT access tokens against the realm's JWKS."""

    def __init__(self, settings: Settings) -> None:
        self._issuer = settings.issuer_url
        self._audience = settings.audience
        # PyJWKClient fetches and caches the signing keys lazily on first use,
        # so constructing it here does not require Keycloak to be reachable yet
        # (important for tests and for booting before Keycloak is up).
        self._jwks_client = PyJWKClient(settings.jwks_uri)

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=self._issuer,
                audience=self._audience,
                options={"require": ["exp", "iat"]},
            )
        except (jwt.PyJWTError, jwt.PyJWKClientError) as exc:
            # Any failure — bad signature, wrong issuer/audience, expired,
            # malformed, or no matching key — means the token is invalid.
            # Returning None makes the SDK respond with 401 Unauthorized.
            _logger.warning("Rejecting bearer token: %s", exc)
            return None

        scope = payload.get("scope", "")
        return AccessToken(
            token=token,
            client_id=payload.get("azp") or payload.get("client_id") or "",
            scopes=scope.split() if isinstance(scope, str) else [],
            expires_at=payload.get("exp"),
            subject=payload.get("sub"),
            claims=payload,
        )


class RequireScope:
    """FastAPI dependency that protects a route with a bearer JWT.

    The MCP endpoint's auth is handled by the MCP SDK; this is the equivalent
    for the plain REST routes (`/api/**`), which the SDK does not cover. It
    reuses :class:`JWTVerifier` to validate the token (signature, issuer,
    audience) and then enforces a single required scope.

    Responses follow the OAuth 2.0 Bearer Token conventions (RFC 6750):
    a missing/invalid token yields 401 with a ``WWW-Authenticate`` header,
    while a valid token lacking the scope yields 403.
    """

    # Pull the credentials from the `Authorization: Bearer <token>` header.
    # auto_error=False lets us emit our own 401 (with WWW-Authenticate) instead
    # of FastAPI's default 403 when the header is absent.
    _bearer = HTTPBearer(auto_error=False)

    def __init__(self, verifier: JWTVerifier, scope: str) -> None:
        self._verifier = verifier
        self._scope = scope

    async def __call__(
        self,
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    ) -> AccessToken:
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing bearer token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access = await self._verifier.verify_token(credentials.credentials)
        if access is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid bearer token",
                headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
            )
        if self._scope not in access.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Token is missing required scope '{self._scope}'",
            )
        return access


def build_auth_settings(settings: Settings) -> AuthSettings:
    """Build the OAuth settings the MCP SDK uses to enforce auth and publish
    Protected Resource Metadata (RFC 9728)."""
    return AuthSettings(
        issuer_url=AnyHttpUrl(settings.issuer_url),
        resource_server_url=settings.mcp_server_url,
        required_scopes=[settings.mcp_required_scope, "offline_access"],
    )


require_api_scope = RequireScope(JWTVerifier(_settings), _settings.api_required_scope)
