import os
import secrets


def generate_embedding_key() -> str:
    return secrets.token_hex(32)


def generate_api_key() -> str:
    return secrets.token_urlsafe(48)


if __name__ == "__main__":
    print("Embedding Key:", generate_embedding_key())
    print("API Key:", generate_api_key())