import os
import logging
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

DEFAULT_KEYS_FOLDER = Path("/etc/keys")
DEFAULT_SIGNING_KEY_FILE = DEFAULT_KEYS_FOLDER / "jwt_rs256_signing_key.pem"
DEFAULT_VERIFYING_KEY_FILE = DEFAULT_KEYS_FOLDER / "jwt_rs256_verifying_key.pem"


def get_jwt_rs256_keys() -> str:
    """Retrieve or generate JWT RS256 signing and verifying keys."""
    signing_key_file = os.environ.get(
        "JWT_SIGNING_KEY_FILE", str(DEFAULT_SIGNING_KEY_FILE)
    )
    verifying_key_file = os.environ.get(
        "JWT_VERIFYING_KEY_FILE", str(DEFAULT_VERIFYING_KEY_FILE)
    )

    signing_key_path = Path(signing_key_file)
    verifying_key_path = Path(verifying_key_file)

    if not signing_key_path.exists() or not verifying_key_path.exists():
        logging.warning(
            """JWT RS256 keys not found, generating new ones.
            In production, please provide your own keys for more security."""
        )
        signing_key_path.parent.mkdir(parents=True, exist_ok=True)
        verifying_key_path.parent.mkdir(parents=True, exist_ok=True)

        generate_rsa_keypair(signing_key_path, verifying_key_path)

    return (
        open(signing_key_path, "r", encoding="utf-8").read(),
        open(verifying_key_path, "r", encoding="utf-8").read(),
    )


def generate_rsa_keypair(private_file: Path, public_file: Path):
    """Generate an RSA keypair and save them to the specified files."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    private_file.write_bytes(private_pem)
    public_file.write_bytes(public_pem)
