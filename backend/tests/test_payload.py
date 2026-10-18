import pytest
from app.core.payload import pack_payload, unpack_payload, PayloadError
from app.core.security import InvalidPasswordError

def test_pack_unpack_text_unencrypted():
    text = "Attack at dawn; coordinate 48.8584, 2.2945."
    packed = pack_payload(text.encode("utf-8"), is_file=False)
    
    stego_data = unpack_payload(packed)
    assert not stego_data.is_file
    assert not stego_data.is_encrypted
    assert stego_data.content.decode("utf-8") == text

def test_pack_unpack_file_with_password():
    file_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDRFakePngBytes"
    packed = pack_payload(
        raw_data=file_bytes,
        is_file=True,
        filename="classified_blueprint.png",
        mime_type="image/png",
        password="TopSecretPassword"
    )
    
    # Attempting to unpack without password should fail
    with pytest.raises(InvalidPasswordError):
        unpack_payload(packed)
        
    # Attempting with wrong password should fail
    with pytest.raises(InvalidPasswordError):
        unpack_payload(packed, password="IncorrectPassword")
        
    # Correct password recovers exact file bytes and metadata
    recovered = unpack_payload(packed, password="TopSecretPassword")
    assert recovered.is_file
    assert recovered.is_encrypted
    assert recovered.filename == "classified_blueprint.png"
    assert recovered.mime_type == "image/png"
    assert recovered.content == file_bytes

def test_crc32_corruption_detection():
    data = b"Critical financial ledger data"
    packed = bytearray(pack_payload(data))
    
    # Corrupt last byte
    packed[-1] ^= 0x01
    
    with pytest.raises(PayloadError, match="integrity check failed"):
        unpack_payload(bytes(packed))

def test_invalid_magic():
    data = b"Some random non-stego bytes"
    with pytest.raises(PayloadError, match="Magic bytes do not match"):
        unpack_payload(data)
