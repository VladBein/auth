from __future__ import annotations

from typing import TypedDict
from datetime import datetime
import json

from .utils import hashing, decode_base64, encode_base64
from auth_user.common.exceptions import InvalidSecurityData


FMT = "%Y-%m-%d %H:%M:%S"
Minute = int


class Tokens(TypedDict):
    access: str
    refresh: str


class JWTToken:
    sub: str
    iat: datetime
    exp: Minute

    @classmethod
    def create_access_and_refresh_tokens(cls, sub: str, iat: datetime) -> Tokens:
        return Tokens(
            access=str(cls(sub, iat, exp=30)),  # ToDo: потом перенесем в настройки
            refresh=str(cls(sub, iat, exp=10080)),
        )

    @classmethod
    def get_token_from_security_data(cls, security_data: str) -> JWTToken:
        try:
            header, payload, signature = security_data.split(".")
        except (IndexError, ValueError):
            raise InvalidSecurityData("Invalid security data")

        hashed_signature = hashing(f"{header}.{payload}")
        if hashed_signature != signature:
            raise InvalidSecurityData("Invalid security data")

        decoded_payload = decode_base64(payload)
        payload = json.loads(decoded_payload.replace("'", "\""))
        return cls(
            payload["sub"],
            datetime.strptime(payload["iat"], FMT),
            payload["exp"]
        )

    def __init__(self, sub, iat, exp):
        self.sub = sub
        self.iat = iat
        self.exp = exp

    def __str__(self):
        header = self._get_header()
        payload = self._get_payload()
        header_base64 = encode_base64(str(header))
        payload_base64 = encode_base64(str(payload))
        signature_hash = hashing(f"{header_base64}.{payload_base64}")
        return f"{header_base64}.{payload_base64}.{signature_hash}"

    def _get_header(self) -> dict:
        return {
            "alg": "HS256",
            "typ": "JWT",
        }

    def _get_payload(self) -> dict:
        return {
            "sub": self.sub,
            "iat": self.iat.strftime(FMT),
            "exp": self.exp,
        }
