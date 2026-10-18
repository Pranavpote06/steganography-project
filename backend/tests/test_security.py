import pytest
from app.core.security import encrypt_payload, decrypt_payload, InvalidPasswordError

def test_encryption_decryption_success():
    secret = b"Confidential Cyber Intelligence Report #9042"
    password = "SuperSecretPassword123!"
    
    encrypted = encrypt_payload(secret, password)
    assert encrypted != secret
    assert len(encrypted) > len(secret)
    
    decrypted = decrypt_payload(encrypted, password)
    assert decrypted == secret

def test_encryption_wrong_password():
    secret = b"Secret payload"
    encrypted = encrypt_payload(secret, "CorrectPassword")
    
    with pytest.raises(InvalidPasswordError):
        decrypt_payload(encrypted, "WrongPassword")

def test_tampered_ciphertext():
    secret = b"Untampered data"
    encrypted = bytearray(encrypt_payload(secret, "Password123"))
    # Flip a byte in the ciphertext
    encrypted[-1] ^= 0xFF
    
    with pytest.raises(InvalidPasswordError):
        decrypt_payload(bytes(encrypted), "Password123")

def test_empty_password():
    with pytest.raises(ValueError):
        encrypt_payload(b"data", "")
