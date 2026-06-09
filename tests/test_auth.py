from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient
from mcp.server.auth.provider import AccessToken

from app.auth import JWTVerifier, RequireScope
from app.config import Settings
from app.main import app


@pytest.fixture
def verifier():
    return JWTVerifier(Settings())


def _access(scopes: list[str]) -> AccessToken:
    return AccessToken(
        token="tok",
        client_id="client",
        scopes=scopes,
        expires_at=None,
        subject="user-123",
        claims={},
    )


def _bearer(token: str = "tok") -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


class TestRequireScope:
    SCOPE = "test-service-api"

    async def test_missing_token_raises_401(self):
        dependency = RequireScope(MagicMock(), self.SCOPE)
        with pytest.raises(HTTPException) as exc_info:
            await dependency(credentials=None)
        assert exc_info.value.status_code == 401
        assert exc_info.value.headers["WWW-Authenticate"].startswith("Bearer")

    async def test_invalid_token_raises_401(self):
        verifier = MagicMock()
        verifier.verify_token = AsyncMock(return_value=None)
        dependency = RequireScope(verifier, self.SCOPE)
        with pytest.raises(HTTPException) as exc_info:
            await dependency(credentials=_bearer())
        assert exc_info.value.status_code == 401

    async def test_token_without_required_scope_raises_403(self):
        verifier = MagicMock()
        verifier.verify_token = AsyncMock(return_value=_access(["openid", "mcp:tools"]))
        dependency = RequireScope(verifier, self.SCOPE)
        with pytest.raises(HTTPException) as exc_info:
            await dependency(credentials=_bearer())
        assert exc_info.value.status_code == 403

    async def test_token_with_required_scope_returns_access(self):
        access = _access(["openid", self.SCOPE])
        verifier = MagicMock()
        verifier.verify_token = AsyncMock(return_value=access)
        dependency = RequireScope(verifier, self.SCOPE)
        assert await dependency(credentials=_bearer()) is access


class TestJWTVerifier:
    async def test_valid_token_maps_claims(self, verifier):
        payload = {
            "azp": "my-client",
            "scope": "openid mcp:tools",
            "exp": 9999999999,
            "sub": "user-123",
        }
        with (
            patch.object(
                verifier._jwks_client,
                "get_signing_key_from_jwt",
                return_value=MagicMock(),
            ),
            patch("app.auth.jwt.decode", return_value=payload),
        ):
            access = await verifier.verify_token("any-token")

        assert access is not None
        assert access.client_id == "my-client"
        assert access.scopes == ["openid", "mcp:tools"]
        assert access.subject == "user-123"
        assert access.claims == payload

    async def test_falls_back_to_client_id_claim(self, verifier):
        # Tokens without `azp` (e.g. some flows) carry `client_id` instead.
        with (
            patch.object(
                verifier._jwks_client,
                "get_signing_key_from_jwt",
                return_value=MagicMock(),
            ),
            patch(
                "app.auth.jwt.decode", return_value={"client_id": "svc", "scope": ""}
            ),
        ):
            access = await verifier.verify_token("any-token")

        assert access is not None
        assert access.client_id == "svc"

    async def test_invalid_token_returns_none(self, verifier):
        with (
            patch.object(
                verifier._jwks_client,
                "get_signing_key_from_jwt",
                return_value=MagicMock(),
            ),
            patch(
                "app.auth.jwt.decode",
                side_effect=jwt.InvalidAudienceError("bad audience"),
            ),
        ):
            assert await verifier.verify_token("any-token") is None

    async def test_unfetchable_signing_key_returns_none(self, verifier):
        with patch.object(
            verifier._jwks_client,
            "get_signing_key_from_jwt",
            side_effect=jwt.PyJWKClientError("no matching key"),
        ):
            assert await verifier.verify_token("any-token") is None


class TestEndpointSecurity:
    # No `with` block / lifespan: the app's MCP session manager is a singleton
    # whose run() is one-shot, so only one test (the smoke test) may enter the
    # lifespan. None of these assertions need the transport running — the /mcp
    # 401 is produced by the auth middleware before the transport is reached.
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_health_is_anonymous(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_messaging_api_requires_authentication(self, client):
        response = client.post(
            "/api/messaging/send",
            json={
                "channel": "WHATSAPP",
                "phoneNumber": "+49 123 456789",
                "message": "hi",
            },
        )
        assert response.status_code == 401
        assert "www-authenticate" in {k.lower() for k in response.headers}

    def test_mcp_requires_authentication(self, client):
        response = client.post(
            "/mcp", json={"jsonrpc": "2.0", "method": "tools/list", "id": 1}
        )
        assert response.status_code == 401
        assert "www-authenticate" in {k.lower() for k in response.headers}

    def test_protected_resource_metadata_is_published(self, client):
        response = client.get("/.well-known/oauth-protected-resource")
        assert response.status_code == 200
        body = response.json()
        assert body["authorization_servers"] == ["http://localhost:8080/realms/master"]
        assert "mcp:tools" in body["scopes_supported"]
