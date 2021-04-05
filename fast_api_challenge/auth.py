import os
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt

from fast_api_challenge.models.api_models import TokenRequestModel, Token

"""
Contains methods for creating and validating JWT Oauth2 tokens.
"""

SECRET_KEY = os.environ.get("auth_issuer_secret_key")  # TODO: Put this in secrets manager
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Creates a JWT access token with the encoded data, valid for the specified time.
    :param data: Body to encode in the token
    :param expires_delta: How long the token should last (timedelta object)
    :return: JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return Token(token=encoded_jwt, type="Bearer")


def authenticate_api_user(token_request: TokenRequestModel):
    """
    "Authenticates" the user with the given name. This could be replaced by taking secrets as parameters and using
    them to authenticate with a secure backend, and also potentially could return scopes to give specific token access
    restrictions
    :param name: Name of the user to authenticate
    :return: Bool
    """
    if token_request.name == os.environ.get("auth_issuer_valid_username"):
        return True
    else:
        return False
