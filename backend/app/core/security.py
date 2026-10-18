import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from typing import Tuple

SALT_SIZE = 16  # 128-bit salt
NONCE_SIZE = 12 # 96-bit standard nonce for AES-GCM
KEY_SIZE = 32   # 256-bit AES key
PBKDF2_ITERATIONS = 100_000

class SecurityError(Exception):
    """Base exception for cryptographic errors."""
    pass

class InvalidPasswordError(SecurityError):
    """Raised when password verification or decryption fails."""
    pass

def derive_key(password: str, salt: bytes) -> bytes:
    """Derives a 256-bit AES key from a passphrase and salt using PBKDF2-HMAC-SHA256."""
    if not password:
        raise ValueError("Password cannot be empty for key derivation")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))

def encrypt_payload(data: bytes, password: str) -> bytes:
    """
    Encrypts arbitrary byte data using AES-256-GCM.
    Returns: [16-byte Salt] + [12-byte Nonce] + [Ciphertext with 16-byte GCM Auth Tag]
    """
    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    key = derive_key(password, salt)
    
    aesgcm = AESGCM(key)
    # Encrypt appends the 16-byte GCM authentication tag automatically
    ciphertext = aesgcm.encrypt(nonce, data, None)
    
    return salt + nonce + ciphertext

def decrypt_payload(encrypted_blob: bytes, password: str) -> bytes:
    """
    Decrypts an AES-256-GCM encrypted payload blob.
    Raises InvalidPasswordError if the password is incorrect or data was tampered with.
    """
    min_required_len = SALT_SIZE + NONCE_SIZE + 16 # salt + nonce + tag
    if len(encrypted_blob) < min_required_len:
        raise InvalidPasswordError("Encrypted payload is malformed or truncated")
    
    salt = encrypted_blob[:SALT_SIZE]
    nonce = encrypted_blob[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
    ciphertext = encrypted_blob[SALT_SIZE + NONCE_SIZE:]
    
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    
    try:
        decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted_data
    except Exception as e:
        raise InvalidPasswordError("Decryption failed. Incorrect password or corrupted payload.") from e
