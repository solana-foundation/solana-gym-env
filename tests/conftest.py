"""Install lightweight stubs so explorer tests run without solana/solders."""

from __future__ import annotations

import sys
from types import ModuleType


class _Fake:
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return _Fake

    def __call__(self, *args, **kwargs):
        return _Fake()

    @staticmethod
    def from_bytes(data):
        return data

    def __bytes__(self):
        return b""


def _mod(name: str) -> ModuleType:
    if name not in sys.modules:
        sys.modules[name] = ModuleType(name)
    return sys.modules[name]


def _missing(module_name: str) -> bool:
    try:
        __import__(module_name)
        return False
    except ImportError:
        return True


def pytest_configure():
    if _missing("base58"):
        base58 = _mod("base58")
        def _b58decode(data):
            if isinstance(data, (bytes, bytearray)):
                return bytes(data)
            raise ValueError("invalid base58")

        base58.b58decode = _b58decode
        base58.b58encode = lambda data: data

    if _missing("gymnasium"):
        gym = _mod("gymnasium")

        class Env:
            metadata = {}

            def reset(self, seed=None, options=None):
                return None, {}

        gym.Env = Env

    if _missing("solana"):
        _mod("solana")
        _mod("solana.rpc")
        async_api = _mod("solana.rpc.async_api")

        class AsyncClient:
            def __init__(self, *args, **kwargs):
                pass

            async def close(self):
                return None

        async_api.AsyncClient = AsyncClient
        async_api.GetTransactionResp = object

    if _missing("solders"):
        _mod("solders")
        tx = _mod("solders.transaction")
        tx.Transaction = _Fake
        tx.VersionedTransaction = _Fake
        keypair = _mod("solders.keypair")
        keypair.Keypair = _Fake
        system = _mod("solders.system_program")
        system.transfer = _Fake()
        system.TransferParams = _Fake
        system.create_nonce_account = _Fake()
        system.create_account = _Fake()
        system.CreateAccountParams = _Fake
        message = _mod("solders.message")
        message.MessageV0 = _Fake
        message.to_bytes_versioned = lambda x: b""
        pubkey = _mod("solders.pubkey")
        pubkey.Pubkey = _Fake
        null_signer = _mod("solders.null_signer")
        null_signer.NullSigner = _Fake
        signature = _mod("solders.signature")
        signature.Signature = _Fake
