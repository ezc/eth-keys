from __future__ import unicode_literals

import pytest

from eth_utils import (
    decode_hex,
    encode_hex,
    keccak,
    is_same_address,
    is_normalized_address,
    is_checksum_address,
    is_canonical_address,
)

from eth_keys import KeyAPI
from eth_keys.backends import NativeECCBackend


MSG = b'message'
MSGHASH = keccak(MSG)


@pytest.fixture
def key_api():
    return KeyAPI(backend=NativeECCBackend())


PK_BYTES = decode_hex(
    '0x58d23b55bc9cdce1f18c2500f40ff4ab7245df9a89505e9b1fa4851f623d241d'
)
ADDRESS = '0xdc544d1aa88ff8bbd2f2aec754b1f1e99e1812fd'


@pytest.fixture
def private_key(key_api):
    return key_api.PrivateKey(PK_BYTES)


def test_signing_from_private_key_obj(key_api, private_key):
    signature = private_key.sign_msg(MSG)

    assert key_api.ecdsa_verify(MSGHASH, signature, private_key.public_key)


def test_hash_signing_from_private_key_obj(key_api, private_key):
    signature = private_key.sign_msg_hash(MSGHASH)

    assert key_api.ecdsa_verify(MSGHASH, signature, private_key.public_key)


def test_recover_from_public_key_class(key_api, private_key):
    signature = key_api.ecdsa_sign(MSGHASH, private_key)
    public_key = key_api.PublicKey.recover_from_msg_hash(MSGHASH, signature)

    assert public_key == key_api.PublicKey.recover_from_msg(MSG, signature)
    assert public_key == private_key.public_key


def test_verify_from_public_key_obj(key_api, private_key):
    signature = key_api.ecdsa_sign(MSGHASH, private_key)
    public_key = private_key.public_key

    assert public_key.verify_msg_hash(MSGHASH, signature)
    assert public_key.verify_msg(MSG, signature)


def test_from_private_for_public_key_class(key_api, private_key):
    public_key = key_api.PublicKey.from_private(private_key)

    assert public_key == private_key.public_key


def test_verify_from_signature_obj(key_api, private_key):
    signature = key_api.ecdsa_sign(MSGHASH, private_key)

    assert signature.verify_msg_hash(MSGHASH, private_key.public_key)
    assert signature.verify_msg(MSG, private_key.public_key)


def test_recover_from_signature_obj(key_api, private_key):
    signature = key_api.ecdsa_sign(MSGHASH, private_key)
    public_key = signature.recover_public_key_from_msg_hash(MSGHASH)

    assert public_key == signature.recover_public_key_from_msg(MSG)
    assert public_key == private_key.public_key


def test_to_address_from_public_key(private_key):
    address = private_key.public_key.to_address()
    assert is_normalized_address(address)
    assert is_same_address(address, ADDRESS)


def test_to_checksum_address_from_public_key(private_key):
    address = private_key.public_key.to_checksum_address()
    assert is_checksum_address(address)
    assert is_same_address(address, ADDRESS)


def test_to_canonical_address_from_public_key(private_key):
    address = private_key.public_key.to_canonical_address()
    assert is_canonical_address(address)
    assert is_same_address(address, ADDRESS)


def test_hex_conversion(private_key):
    public_key = private_key.public_key
    signature = private_key.sign_msg(b'message')

    assert hex(public_key) == encode_hex(public_key.to_bytes())
    assert hex(private_key) == encode_hex(private_key.to_bytes())
    assert hex(signature) == encode_hex(signature.to_bytes())

    assert public_key.to_hex() == encode_hex(public_key.to_bytes())
    assert private_key.to_hex() == encode_hex(private_key.to_bytes())
    assert signature.to_hex() == encode_hex(signature.to_bytes())


def test_bytes_conversion(key_api, private_key):
    public_key = private_key.public_key
    signature = private_key.sign_msg(b'message')

    assert public_key.to_bytes() == public_key._raw_key
    assert private_key.to_bytes() == private_key._raw_key
    assert signature.to_bytes() == key_api.Signature(signature.to_bytes()).to_bytes()
