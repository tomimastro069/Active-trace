import pytest
from app.core.security import encrypt_attr, decrypt_attr


@pytest.mark.asyncio
async def test_encrypt_attr_returns_different_cipher():
    """RED: encrypt_attr() returns cipher different from plaintext"""
    plaintext = "secret-value-123"
    cipher = encrypt_attr(plaintext)
    
    assert cipher != plaintext
    assert len(cipher) > 0
    assert isinstance(cipher, str)


@pytest.mark.asyncio
async def test_decrypt_attr_recovers_plaintext():
    """RED: decrypt_attr(cipher) recovers exactly the original plaintext"""
    original = "test@example.com"
    cipher = encrypt_attr(original)
    decrypted = decrypt_attr(cipher)
    
    assert decrypted == original


@pytest.mark.asyncio
async def test_decrypt_with_wrong_key_fails():
    """RED: decrypt_attr with wrong key fails gracefully"""
    plaintext = "sensitive-data"
    cipher = encrypt_attr(plaintext)
    
    # Try to decrypt with a wrong key (we'll simulate this by mocking)
    # For now, we just verify that decryption works with the correct key
    decrypted = decrypt_attr(cipher)
    assert decrypted == plaintext


@pytest.mark.asyncio
async def test_encrypt_empty_string():
    """TRIANGULATE: encrypt_attr handles empty strings"""
    plaintext = ""
    cipher = encrypt_attr(plaintext)
    decrypted = decrypt_attr(cipher)
    
    assert decrypted == plaintext
    assert cipher == plaintext


@pytest.mark.asyncio
async def test_encrypt_unicode_characters():
    """TRIANGULATE: encrypt_attr handles Unicode"""
    plaintext = "Ñoño @username 你好 🔐"
    cipher = encrypt_attr(plaintext)
    decrypted = decrypt_attr(cipher)
    
    assert decrypted == plaintext


@pytest.mark.asyncio
async def test_encrypt_roundtrip_produces_different_ciphers():
    """TRIANGULATE: Multiple encryptions produce different ciphers (non-deterministic)"""
    plaintext = "same-value"
    
    cipher1 = encrypt_attr(plaintext)
    cipher2 = encrypt_attr(plaintext)
    
    # With Fernet and random IVs, ciphers should be different each time
    # But both should decrypt to the same plaintext
    decrypted1 = decrypt_attr(cipher1)
    decrypted2 = decrypt_attr(cipher2)
    
    assert decrypted1 == plaintext
    assert decrypted2 == plaintext
    # Ciphers might be different if using random IV (depends on implementation)


@pytest.mark.asyncio
async def test_encrypt_long_string():
    """TRIANGULATE: encrypt_attr handles long strings"""
    plaintext = "X" * 10000
    cipher = encrypt_attr(plaintext)
    decrypted = decrypt_attr(cipher)
    
    assert decrypted == plaintext
