"""Security utilities for password hashing and token generation."""
import secrets
from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from services.shared.config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    # Bcrypt has a 72 byte limit
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password to verify against
        
    Returns:
        True if password matches, False otherwise
    """
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None,
    tenant_id: Optional[UUID] = None,
    is_super_admin: bool = False,
) -> str:
    """Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta
        tenant_id: Tenant ID to include in token (optional)
        is_super_admin: Whether user is super admin (optional)
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
    
    # Adicionar tenant_id e is_super_admin ao token
    if tenant_id:
        to_encode["tenant_id"] = str(tenant_id)
    if is_super_admin:
        to_encode["is_super_admin"] = True
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def create_refresh_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT refresh token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.jwt_refresh_token_expire_days
        )
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Decoded token payload
        
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError as e:
        raise JWTError(f"Invalid token: {str(e)}")


def generate_api_token() -> str:
    """Generate a secure random API token.
    
    Returns:
        Random token string
    """
    return secrets.token_urlsafe(32)


def hash_api_token(token: str) -> str:
    """Hash an API token for storage.
    
    Args:
        token: Plain API token
        
    Returns:
        Hashed token
    """
    token_bytes = token.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(token_bytes, salt)
    return hashed.decode('utf-8')


def verify_api_token(plain_token: str, hashed_token: str) -> bool:
    """Verify an API token against a hash.
    
    Args:
        plain_token: Plain API token
        hashed_token: Hashed token to verify against
        
    Returns:
        True if token matches, False otherwise
    """
    token_bytes = plain_token.encode('utf-8')[:72]
    hashed_bytes = hashed_token.encode('utf-8')
    return bcrypt.checkpw(token_bytes, hashed_bytes)
