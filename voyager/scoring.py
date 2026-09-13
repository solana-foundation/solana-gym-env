"""Pure unique-instruction scoring helpers.

These functions have no RPC, validator, or LLM dependencies so reward
logic can be tested offline.
"""

from __future__ import annotations

import base64
import os
from typing import Any, Iterable, Mapping, Sequence

try:
    import base58
except ImportError:  # pragma: no cover - optional in unit tests
    base58 = None


MEMO_V2 = "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr"
MEMO_V1 = "Memo1UhkJRfHyvLMcVucJwxXeuD728EqVDDwQDxFMNo"

DEFAULT_EXCLUDED_PROGRAMS: tuple[str, ...] = (MEMO_V2, MEMO_V1)

_UNSET = object()


def decode_ix_data(data: Any) -> bytes:
    """Normalize instruction data from bytes, int lists, base58, or base64."""
    if data is None:
        return b""
    if isinstance(data, bytes):
        return data
    if isinstance(data, bytearray):
        return bytes(data)
    if isinstance(data, memoryview):
        return bytes(data)
    if isinstance(data, (list, tuple)):
        try:
            return bytes(data)
        except (ValueError, TypeError):
            return b""
    if isinstance(data, str):
        if not data:
            return b""
        if base58 is not None:
            try:
                return base58.b58decode(data)
            except Exception:
                pass
        try:
            return base64.b64decode(data, validate=True)
        except Exception:
            try:
                return base64.b64decode(data)
            except Exception:
                return data.encode("utf-8")
    return b""


def instruction_discriminator(data: Any) -> int:
    """First byte of instruction data, or 0 when data is empty."""
    decoded = decode_ix_data(data)
    return decoded[0] if decoded else 0


def normalize_program_id(program_id: Any) -> str:
    return str(program_id)


def unique_instruction_key(program_id: Any, data: Any) -> tuple[str, int]:
    return (normalize_program_id(program_id), instruction_discriminator(data))


def max_unique_per_program_from_env(default: int = 32) -> int | None:
    """Read ``SCORE_MAX_UNIQUE_PER_PROGRAM``; unset uses ``default``."""
    raw = os.environ.get("SCORE_MAX_UNIQUE_PER_PROGRAM")
    if raw is None:
        return default
    raw = raw.strip()
    if not raw or raw.lower() in {"none", "unlimited", "0"}:
        return None
    return int(raw)


def _program_unique_count(seen: dict[tuple[str, int], bool], program_id: str) -> int:
    return sum(1 for prog, _ in seen if prog == program_id)


def _is_spam_shaped(ix: Mapping[str, Any]) -> bool:
    """Zero-account ix with non-empty data when account metas are present."""
    accounts = ix.get("accounts")
    if accounts is None:
        return False
    data = decode_ix_data(ix.get("data"))
    return len(accounts) == 0 and len(data) > 0


def collect_ordered_instructions(
    top_level: Sequence[Mapping[str, Any]],
    inner_by_index: Mapping[int, Sequence[Mapping[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    """Flatten top-level + inner instructions.

    Missing inner-instruction indexes are treated as empty. This is the
    sandbox scoring equivalent of Solana's ordered instruction list.
    """
    inner_by_index = inner_by_index or {}
    ordered: list[dict[str, Any]] = []
    for idx, ix in enumerate(top_level):
        entry: dict[str, Any] = {
            "program_id": ix["program_id"],
            "data": decode_ix_data(ix.get("data")),
        }
        if "accounts" in ix:
            entry["accounts"] = ix["accounts"]
        ordered.append(entry)
        for inner in inner_by_index.get(idx, []) or []:
            inner_entry: dict[str, Any] = {
                "program_id": inner["program_id"],
                "data": decode_ix_data(inner.get("data")),
            }
            if "accounts" in inner:
                inner_entry["accounts"] = inner["accounts"]
            ordered.append(inner_entry)
    return ordered


def discovery_reward(
    instructions: Iterable[Mapping[str, Any]],
    seen: dict[tuple[str, int], bool],
    allowed_programs: Sequence[str] | None = None,
    excluded_programs: Sequence[str] | object = _UNSET,
    max_unique_per_program: int | None = 32,
    apply_spam_filter: bool = True,
) -> int:
    """+1 for each new (program_id, discriminator) pair under fair rules.

    ``seen`` is mutated in place so repeated instructions across
    transactions are not double-counted.

    ``excluded_programs`` defaults to Memo v1/v2. Pass ``[]`` to disable
    exclusions (legacy include-all). Exclusions apply only when
    ``allowed_programs`` is not set.
    """
    if excluded_programs is _UNSET:
        excluded = set(DEFAULT_EXCLUDED_PROGRAMS)
    else:
        excluded = set(excluded_programs)  # type: ignore[arg-type]

    allowed = set(allowed_programs) if allowed_programs else None
    reward = 0
    for ix in instructions:
        prog = normalize_program_id(ix["program_id"])
        if allowed is not None:
            if prog not in allowed:
                continue
        elif excluded and prog in excluded:
            continue

        if apply_spam_filter and _is_spam_shaped(ix):
            continue

        key = unique_instruction_key(prog, ix.get("data"))
        if key in seen:
            continue

        if (
            max_unique_per_program is not None
            and _program_unique_count(seen, prog) >= max_unique_per_program
        ):
            continue

        seen[key] = True
        reward += 1
    return reward


def discovery_reward_unfiltered(
    instructions: Iterable[Mapping[str, Any]],
    seen: dict[tuple[str, int], bool],
    allowed_programs: Sequence[str] | None = None,
) -> int:
    """Legacy scoring: no exclusions, cap, or spam filter."""
    return discovery_reward(
        instructions,
        seen,
        allowed_programs=allowed_programs,
        excluded_programs=[],
        max_unique_per_program=None,
        apply_spam_filter=False,
    )


def unique_instructions_by_program(
    instructions: Iterable[Mapping[str, Any]],
) -> dict[str, list[int]]:
    grouped: dict[str, list[int]] = {}
    for ix in instructions:
        prog = normalize_program_id(ix["program_id"])
        disc = instruction_discriminator(ix.get("data"))
        grouped.setdefault(prog, [])
        grouped[prog].append(disc)
    return grouped
