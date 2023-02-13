import hashlib
import base64


def hashing(value: str) -> str:
    salt = "22gyJL22"
    hash_bytes = hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=value.encode("utf-8"),
        salt=salt.encode("utf-8"),
        iterations=100000
    )
    return hash_bytes.hex()


def encode_base64(value: str) -> str:
    value_bytes = value.encode("utf-8")
    value_base64 = base64.b64encode(value_bytes).decode()
    return value_base64


def decode_base64(value: str) -> str:
    value_base64_bytes = value.encode("utf-8")
    value_bytes = base64.b64decode(value_base64_bytes).decode("utf-8")
    return value_bytes
