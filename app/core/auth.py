"""FastAPI auth dependencies — extract and validate JWT from requests.

Usage in a router
-----------------
from app.core.auth import get_current_user, require_role

# Any authenticated user:
async def my_endpoint(_user: dict = Depends(get_current_user)): ...

# Only specific roles:
async def admin_endpoint(_user: dict = Depends(require_role("admin"))): ...
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_access_token
from app.domain.exceptions import TokenExpiredError, TokenInvalidError

# Tells FastAPI to expect an Authorization: Bearer <token> header.
# auto_error=True (default) returns 403 automatically if the header is missing.
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """Extract and validate the JWT bearer token.

    Returns the decoded token payload dict (contains ``sub``, ``email``,
    ``role``, etc.) so downstream handlers can use the caller's identity.

    Raises
    ------
    HTTP 401
        When the token is missing, expired, or has an invalid signature.
    """
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        return payload
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except TokenInvalidError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(*roles: str):
    """Dependency factory that enforces one of the given roles.

    Parameters
    ----------
    *roles:
        One or more role strings that are permitted to access the endpoint.
        Example: ``require_role("admin", "doctor")``.

    Returns
    -------
    Callable
        A FastAPI-compatible dependency that resolves to the token payload
        dict on success, or raises HTTP 403 when the caller's role is not
        in the allowed list.

    Usage
    -----
    async def create_patient(
        dto: PatientCreateDTO,
        uow=Depends(get_unit_of_work),
        _user: dict = Depends(require_role("admin", "doctor")),
    ): ...
    """
    def _check_role(user: dict = Depends(get_current_user)) -> dict:
        caller_role = user.get("role")
        if caller_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Role '{caller_role}' is not authorized for this action. "
                    f"Required: {list(roles)}."
                ),
            )
        return user
    return _check_role
