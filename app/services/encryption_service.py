import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class EncryptionService:
    """
    AES-256-GCM symmetric encryption for temporary PDF blobs.

    The encryption key is NEVER stored server-side. It is embedded in the
    owner's download URL only (base64url query parameter). The server stores
    only the ciphertext and the 12-byte GCM nonce.
    """

    @staticmethod
    def generate_key() -> bytes:
        return os.urandom(32)  # 256-bit key

    @staticmethod
    def encrypt(plaintext: bytes, key: bytes) -> tuple[bytes, bytes]:
        """
        Encrypt plaintext with AES-256-GCM.
        Returns (ciphertext_with_tag, nonce).
        Store both ciphertext and nonce; discard key immediately after embedding in URL.
        """
        nonce = os.urandom(12)  # 96-bit nonce recommended for GCM
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        return ciphertext, nonce

    @staticmethod
    def decrypt(ciphertext: bytes, nonce: bytes, key: bytes) -> bytes:
        """
        Decrypt ciphertext. Raises cryptography.exceptions.InvalidTag if key/nonce mismatch.
        """
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None)

    @staticmethod
    def key_to_url_safe(key: bytes) -> str:
        return base64.urlsafe_b64encode(key).decode()

    @staticmethod
    def key_from_url_safe(encoded: str) -> bytes:
        return base64.urlsafe_b64decode(encoded.encode())
