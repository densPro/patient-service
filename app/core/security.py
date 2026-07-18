"""JWT verification utility for patient-management-service.

Decodes access tokens locally using the shared JWT_SECRET_KEY —
no HTTP call to identity-service is required per request.
"""

from __future__ import annotations

import jwt

from app.config import settings
from app.domain.exceptions import TokenExpiredError, TokenInvalidError


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token.

    Parameters
    ----------
    token:
        Raw JWT string from the ``Authorization: Bearer <token>`` header.

    Returns
    -------
    dict
        The decoded payload containing at minimum ``sub``, ``email``,
        ``role``, ``type``, ``exp``, and ``iat`` claims.

    Raises
    ------
    TokenExpiredError
        When the token's ``exp`` claim is in the past.
    TokenInvalidError
        When the token cannot be decoded (bad signature, malformed, etc.).
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise TokenExpiredError() from exc
    except jwt.PyJWTError as exc:
        raise TokenInvalidError(str(exc)) from exc
