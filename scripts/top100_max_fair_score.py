#!/usr/bin/env python3
"""Estimate max fair discovery score from the top-100 most-used Solana programs.

Fair scoring rules (see voyager/scoring.py):
  +1 per unique (program_id, first_byte_of_ix_data) on successful txs
  Memo v1/v2 excluded by default
  Cap: max_unique_per_program=32 (SCORE_MAX_UNIQUE_PER_PROGRAM)
  First-pass ceiling: assume saturating the cap → ≤ 32 × (#non-Memo in top 100)

Usage ranking source (reproducible, not invented):
  1. Live: sample recent mainnet blocks via public Solana RPC getBlock
  2. Fallback: checked-in docs/top100_programs_snapshot.json (source + date documented)

Optional IDL / known-instruction ceiling uses documented native/SPL instruction
tags (first-byte = enum index). Unknown programs contribute 32 to theoretical_cap
only; their idl_known ceiling is left blank.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from voyager.scoring import (  # noqa: E402
    DEFAULT_EXCLUDED_PROGRAMS,
    MEMO_V1,
    MEMO_V2,
    max_unique_per_program_from_env,
)

DEFAULT_SNAPSHOT = ROOT / "docs" / "top100_programs_snapshot.json"
DEFAULT_DOCS = ROOT / "docs" / "top100-max-fair-score.md"
DEFAULT_RPC = "https://api.mainnet-beta.solana.com"
GROK_FAIR = 66
GROK_RAW = 70

# Human-readable labels for common programs (explorer + well-known DeFi).
# Rankings themselves always come from RPC/snapshot — never invented here.
PROGRAM_NAMES: dict[str, str] = {
    "11111111111111111111111111111111": "System Program",
    "Vote111111111111111111111111111111111111111": "Vote Program",
    "Stake11111111111111111111111111111111111111": "Stake Program",
    "Config1111111111111111111111111111111111111": "Config Program",
    "ComputeBudget111111111111111111111111111111": "Compute Budget",
    "AddressLookupTab1e1111111111111111111111111": "Address Lookup Table",
    "BPFLoaderUpgradeab1e11111111111111111111111": "BPF Upgradeable Loader",
    "Ed25519SigVerify111111111111111111111111111": "Ed25519 SigVerify",
    "KeccakSecp256k11111111111111111111111111111": "Secp256k1 SigVerify",
    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "SPL Token",
    "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb": "Token-2022",
    "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL": "Associated Token Account",
    MEMO_V1: "Memo v1",
    MEMO_V2: "Memo v2",
    "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter Aggregator v6",
    "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter Aggregator v4",
    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "pump.fun",
    "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA": "Pump AMM",
    "pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ": "Pump Fees",
    "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CLMM",
    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium AMM v4",
    "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "Raydium CPMM",
    "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
    "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo": "Meteora DLMM",
    "cpamdpZCGKUy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG": "Meteora DAMM v2",
    "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN": "Dynamic Bonding Curve",
    "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s": "Metaplex Token Metadata",
    "noopb9bkMVfRPU8AsbpTUg8AQkHtKwMYZiFUjNRtMmV": "Noop",
    "SPoo1Ku8WFXoNDMHPsrGSTSG1Y47rzgn41SLUNakuHy": "Stake Pool",
    "MarBmsSgKXdrN1egZf5sqe1TMai9K1rChYNDJgjq7aD": "Marinade",
    "TessVdML9pBGgG9yGks7o4HewRaXVAMuoVj4x83GLQH": "TesseraV",
    "FLASHX8DrLbgeR8FcfNV1F5krxYcYMUdBkrP1EPBtxB9": "Flash Loan Aggregator",
    "LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj": "Raydium LaunchLab",
    "rec5EKMGg6MxZYaMdyBfgwp4d5rB9T1VQH5pJv5LtFJ": "Pyth Receiver",
    "pythWSnswVUd12oZpeFP8e9CVaEqJg25g1Vtc2biRsT": "Pyth Oracle",
    "CoREENxT6tW1HoK8ypY1SxRMZTcVPm7R94rH4PZNhX7d": "MPL Core",
    "mmm3XBJg5gk8XJxEKBvdgptZz6SgK4tXvn36sodowMc": "MPL Magic Eden MMM",
    "L2TExMFKdjpN9kozasaurPirfHy9P8sbXoAN1qA3S95": "Lighthouse",
    "DJEtUsoaPemxBwXTMEeizAsY2KFTytRQ3dixWRCcndd": "Drift Vaults",
    "dRiftyHA39MWEi3m9aunc5MzRF1JYuBsbn6VPcn33UH": "Drift Protocol",
}

# Documented native/SPL instruction first-byte catalogs (enum index packing).
# Values = distinct first-byte tags that can succeed under normal encoding.
KNOWN_FIRST_BYTE_COUNTS: dict[str, int] = {
    "11111111111111111111111111111111": 13,  # SystemInstruction
    "Vote111111111111111111111111111111111111111": 16,  # VoteInstruction
    "Stake11111111111111111111111111111111111111": 18,  # StakeInstruction
    "ComputeBudget111111111111111111111111111111": 5,  # ComputeBudgetInstruction
    "AddressLookupTab1e1111111111111111111111111": 5,  # ProgramInstruction
    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": 28,  # TokenInstruction (classic)
    "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb": 48,  # Token-2022 (≥32 → cap)
    "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL": 3,  # Create/CreateIdempotent/RecoverNested
}


def fair_ceiling(known_first_bytes: int | None, cap: int) -> int:
    if known_first_bytes is None:
        return cap
    return min(cap, known_first_bytes)


def _rpc(rpc_url: str, method: str, params: list[Any]) -> Any:
    body = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    ).encode()
    req = urllib.request.Request(
        rpc_url, data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        payload = json.loads(resp.read())
    if "error" in payload:
        raise RuntimeError(payload["error"])
    return payload["result"]


def _account_keys(msg: dict[str, Any], meta: dict[str, Any]) -> list[str]:
    keys: list[str] = []
    for key in msg.get("accountKeys") or []:
        keys.append(key if isinstance(key, str) else key.get("pubkey"))
    loaded = (meta or {}).get("loadedAddresses") or {}
    keys.extend(loaded.get("writable") or [])
    keys.extend(loaded.get("readonly") or [])
    return keys


def fetch_top_programs_via_rpc(
    rpc_url: str,
    *,
    target_blocks: int = 80,
    slot_stride: int = 5,
) -> dict[str, Any]:
    """Rank programs by successful-tx presence in a recent getBlock sample."""
    tip = _rpc(rpc_url, "getSlot", [])
    ix_counts: Counter[str] = Counter()
    tx_counts: Counter[str] = Counter()
    slots_used: list[int] = []
    blocks_ok = 0
    fetched_at = datetime.now(timezone.utc).isoformat()
    start_slot = tip - 10

    for slot in range(start_slot, start_slot - target_blocks * slot_stride * 3, -slot_stride):
        try:
            block = _rpc(
                rpc_url,
                "getBlock",
                [
                    slot,
                    {
                        "encoding": "json",
                        "transactionDetails": "full",
                        "rewards": False,
                        "maxSupportedTransactionVersion": 0,
                    },
                ],
            )
        except (RuntimeError, urllib.error.URLError, TimeoutError, OSError):
            time.sleep(0.35)
            continue
        if not block:
            continue
        blocks_ok += 1
        slots_used.append(slot)
        for tx in block.get("transactions") or []:
            meta = tx.get("meta") or {}
            if meta.get("err"):
                continue
            msg = (tx.get("transaction") or {}).get("message") or {}
            keys = _account_keys(msg, meta)

            def pid_of(ix: dict[str, Any]) -> str | None:
                idx = ix["programIdIndex"]
                return keys[idx] if idx < len(keys) else None

            seen: set[str] = set()
            for ix in msg.get("instructions") or []:
                pid = pid_of(ix)
                if not pid:
                    continue
                ix_counts[pid] += 1
                seen.add(pid)
            for group in meta.get("innerInstructions") or []:
                for ix in group.get("instructions") or []:
                    pid = pid_of(ix)
                    if not pid:
                        continue
                    ix_counts[pid] += 1
                    seen.add(pid)
            for pid in seen:
                tx_counts[pid] += 1
        time.sleep(0.08)
        if blocks_ok >= target_blocks:
            break

    if blocks_ok < max(10, target_blocks // 4):
        raise RuntimeError(
            f"RPC sample too small ({blocks_ok} blocks); use --snapshot"
        )

    programs = [
        {
            "rank": i,
            "program_id": pid,
            "tx_count": n,
            "ix_count": ix_counts[pid],
        }
        for i, (pid, n) in enumerate(tx_counts.most_common(120), 1)
    ]
    return {
        "source": "solana_rpc_getBlock_sample",
        "source_detail": (
            "Public Solana RPC getBlock sampling of recent mainnet blocks. "
            "Ranked by successful transactions that invoke the program "
            "(top-level + inner instructions)."
        ),
        "rpc": rpc_url,
        "fetched_at_utc": fetched_at,
        "tip_slot_at_start": tip,
        "blocks_sampled": blocks_ok,
        "slot_min": min(slots_used) if slots_used else None,
        "slot_max": max(slots_used) if slots_used else None,
        "metric": "successful_tx_count_containing_program",
        "secondary_metric": "instruction_invocation_count",
        "programs": programs,
    }


def load_snapshot(path: Path) -> dict[str, Any]:
    with path.open() as f:
        data = json.load(f)
    if not data.get("programs"):
        raise ValueError(f"snapshot missing programs: {path}")
    return data


def select_top100(programs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(
        programs,
        key=lambda p: (
            -int(p.get("tx_count") or p.get("ix_count") or 0),
            p.get("program_id", ""),
        ),
    )
    # Re-rank 1..N from the usage source (may already be ranked).
    out = []
    for i, row in enumerate(ordered[:100], 1):
        item = dict(row)
        item["rank"] = i
        out.append(item)
    return out


def analyze(
    top100: list[dict[str, Any]],
    *,
    cap: int,
    excluded: set[str],
) -> dict[str, Any]:
    rows = []
    for row in top100:
        pid = row["program_id"]
        excluded_here = pid in excluded
        known = KNOWN_FIRST_BYTE_COUNTS.get(pid)
        ceiling = 0 if excluded_here else fair_ceiling(None, cap)  # saturating
        idl_ceiling = (
            None
            if excluded_here or known is None
            else fair_ceiling(known, cap)
        )
        notes = []
        if excluded_here:
            notes.append("excluded (Memo)")
            ceiling = 0
        elif known is not None:
            notes.append(f"known_first_bytes={known}")
        else:
            notes.append("unknown ix catalog → assume cap")
        rows.append(
            {
                "rank": row["rank"],
                "program_id": pid,
                "name": PROGRAM_NAMES.get(pid) or row.get("name") or "",
                "tx_count": int(row.get("tx_count") or 0),
                "ix_count": int(row.get("ix_count") or 0),
                "fair_ceiling_32": ceiling,
                "idl_known_cap": idl_ceiling,
                "excluded": excluded_here,
                "notes": "; ".join(notes),
            }
        )

    scoring = [r for r in rows if not r["excluded"]]
    n = len(scoring)
    theoretical_cap = cap * n
    idl_parts = [r["idl_known_cap"] for r in scoring if r["idl_known_cap"] is not None]
    unknown = n - len(idl_parts)
    idl_known_cap = (
        sum(idl_parts) + unknown * cap if scoring else 0
    )  # unknowns still counted at cap for an upper bound
    idl_known_only = sum(idl_parts)  # sum over programs with catalogs only

    return {
        "rows": rows,
        "n_top100": len(rows),
        "n_scoring": n,
        "n_excluded_memo": len(rows) - n,
        "cap": cap,
        "theoretical_cap": theoretical_cap,
        "idl_known_cap_upper": idl_known_cap,
        "idl_known_only_sum": idl_known_only,
        "idl_known_program_count": len(idl_parts),
        "idl_unknown_program_count": unknown,
    }


def print_table(analysis: dict[str, Any]) -> None:
    print(
        f"{'rank':>4}  {'program_id':<44}  {'name':<28}  "
        f"{'tx':>8}  {'ceil':>4}  {'idl':>4}  notes"
    )
    print("-" * 120)
    for r in analysis["rows"]:
        idl = "" if r["idl_known_cap"] is None else str(r["idl_known_cap"])
        name = (r["name"] or "")[:28]
        print(
            f"{r['rank']:4d}  {r['program_id']:<44}  {name:<28}  "
            f"{r['tx_count']:8d}  {r['fair_ceiling_32']:4d}  {idl:>4}  {r['notes']}"
        )
    print("-" * 120)
    print(
        f"N_scoring={analysis['n_scoring']}  "
        f"theoretical_cap={analysis['theoretical_cap']}  "
        f"idl_known_cap_upper={analysis['idl_known_cap_upper']}  "
        f"(known-only sum={analysis['idl_known_only_sum']} over "
        f"{analysis['idl_known_program_count']} programs)"
    )
    pct = 100.0 * GROK_FAIR / analysis["theoretical_cap"] if analysis["theoretical_cap"] else 0.0
    print(
        f"Grok fair {GROK_FAIR} / theoretical_cap {analysis['theoretical_cap']} "
        f"= {pct:.2f}%"
    )


def write_markdown(
    path: Path,
    *,
    source: dict[str, Any],
    analysis: dict[str, Any],
) -> None:
    theoretical = analysis["theoretical_cap"]
    pct = 100.0 * GROK_FAIR / theoretical if theoretical else 0.0
    lines = [
        "# Top-100 max fair score estimate",
        "",
        "## Verdict",
        "",
        f"| Metric | Value |",
        f"|--------|------:|",
        f"| **theoretical_cap** (`32 × N`) | **{theoretical}** |",
        f"| N (top-100 minus Memo v1/v2) | {analysis['n_scoring']} |",
        f"| Memo excluded from top-100 | {analysis['n_excluded_memo']} |",
        f"| Per-program cap | {analysis['cap']} |",
        f"| idl_known_cap (upper; unknowns@cap) | {analysis['idl_known_cap_upper']} |",
        f"| idl_known_only (sum over cataloged) | {analysis['idl_known_only_sum']} "
        f"({analysis['idl_known_program_count']} programs) |",
        f"| Grok fair / raw | **{GROK_FAIR}** / {GROK_RAW} |",
        f"| **Grok fair ÷ theoretical_cap** | **{pct:.2f}%** |",
        "",
        "## Method",
        "",
        "Fair scoring reuses `voyager/scoring.py`:",
        "",
        "- `+1` per unique `(program_id, first_byte_of_ix_data)` on successful txs",
        "- Memo v1/v2 in `DEFAULT_EXCLUDED_PROGRAMS` → fair contribution **0**",
        "- Cap `max_unique_per_program=32` (`SCORE_MAX_UNIQUE_PER_PROGRAM`)",
        "- Zero-account spam-shaped ixs do not score when metas are present",
        "- Per-program fair ceiling = `min(32, distinct_first_bytes_that_can_succeed)`",
        "- **First-pass ceiling** assumes saturating the cap → "
        "`theoretical_cap = 32 × (# non-Memo programs in top 100)`",
        "",
        "No Memo farms. Rankings are **not invented**.",
        "",
        "## Source",
        "",
        f"- **kind:** `{source.get('source')}`",
        f"- **detail:** {source.get('source_detail', '')}",
        f"- **fetched_at_utc:** `{source.get('fetched_at_utc', 'n/a')}`",
        f"- **rpc:** `{source.get('rpc', 'n/a')}`",
        f"- **blocks_sampled:** {source.get('blocks_sampled', 'n/a')}",
        f"- **slot range:** {source.get('slot_min', '?')} … {source.get('slot_max', '?')} "
        f"(tip at start `{source.get('tip_slot_at_start', '?')}`)",
        f"- **metric:** `{source.get('metric')}` "
        f"(secondary `{source.get('secondary_metric')}`)",
        "",
        "Refresh:",
        "",
        "```bash",
        "PYTHONPATH=. python3 scripts/top100_max_fair_score.py --refresh --write-docs",
        "# or use the checked-in snapshot only:",
        "PYTHONPATH=. python3 scripts/top100_max_fair_score.py --snapshot docs/top100_programs_snapshot.json --write-docs",
        "```",
        "",
        "Checked-in snapshot: [`docs/top100_programs_snapshot.json`](./top100_programs_snapshot.json).",
        "",
        "If live RPC refresh fails (rate limits / network), keep using the snapshot JSON;",
        "do not invent a ranking.",
        "",
        "## Comparison to Grok fair climb",
        "",
        f"Canonical Grok fair climb: fair **{GROK_FAIR}** / raw **{GROK_RAW}** / memo **0**.",
        "",
        f"Against this top-100 first-pass ceiling (**{theoretical}**), Grok reached "
        f"**{pct:.2f}%** of the saturating theoretical max. That ceiling is an "
        f"**upper bound** (many programs cannot expose 32 distinct successful "
        f"first-bytes; Anchor discriminators also collide on byte0).",
        "",
        "## Per-program table (top 100 by usage)",
        "",
        "| rank | program_id | name | tx_count | fair_ceiling_32 | idl_known_cap | notes |",
        "|-----:|------------|------|---------:|----------------:|--------------:|-------|",
    ]
    for r in analysis["rows"]:
        idl = "" if r["idl_known_cap"] is None else str(r["idl_known_cap"])
        lines.append(
            f"| {r['rank']} | `{r['program_id']}` | {r['name'] or '—'} | "
            f"{r['tx_count']} | {r['fair_ceiling_32']} | {idl or '—'} | {r['notes']} |"
        )
    lines.extend(
        [
            "",
            "## Notes on `idl_known_cap`",
            "",
            "Cataloged counts come from public native/SPL instruction enums "
            "(System, Vote, Stake, ComputeBudget, ALT, Token, Token-2022, ATA) "
            "where the first data byte is the instruction tag. "
            "Token-2022 has >32 tags → capped at 32. "
            "Programs without a catalog still count as **32** in "
            "`idl_known_cap_upper` so that figure remains an upper bound, not a "
            "tight IDL sum. `idl_known_only` is the sum over cataloged programs alone.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--snapshot",
        type=Path,
        default=DEFAULT_SNAPSHOT,
        help="Checked-in usage snapshot JSON (used by default / on refresh failure)",
    )
    p.add_argument(
        "--refresh",
        action="store_true",
        help="Fetch a fresh ranking via public Solana RPC getBlock sampling",
    )
    p.add_argument(
        "--save-snapshot",
        type=Path,
        default=None,
        help="When refreshing, also write snapshot JSON to this path "
        f"(default: {DEFAULT_SNAPSHOT})",
    )
    p.add_argument("--rpc", default=DEFAULT_RPC, help="Solana JSON-RPC URL")
    p.add_argument("--blocks", type=int, default=80, help="Blocks to sample on refresh")
    p.add_argument(
        "--write-docs",
        action="store_true",
        help=f"Write {DEFAULT_DOCS}",
    )
    p.add_argument("--docs-path", type=Path, default=DEFAULT_DOCS)
    p.add_argument(
        "--cap",
        type=int,
        default=None,
        help="Override per-program unique cap (default: env/scoring helper = 32)",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    cap = args.cap if args.cap is not None else (max_unique_per_program_from_env() or 32)
    excluded = set(DEFAULT_EXCLUDED_PROGRAMS)

    source: dict[str, Any] | None = None
    if args.refresh:
        try:
            print(f"Refreshing top programs via RPC {args.rpc} …", file=sys.stderr)
            source = fetch_top_programs_via_rpc(args.rpc, target_blocks=args.blocks)
            out = args.save_snapshot or args.snapshot
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(source, indent=2) + "\n")
            print(f"Wrote snapshot {out}", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001 - fall back is intentional
            print(f"Live refresh failed ({exc}); loading snapshot.", file=sys.stderr)
            source = None

    if source is None:
        if not args.snapshot.exists():
            print(f"No snapshot at {args.snapshot}", file=sys.stderr)
            return 1
        source = load_snapshot(args.snapshot)
        print(f"Loaded snapshot {args.snapshot}", file=sys.stderr)

    top100 = select_top100(list(source["programs"]))
    analysis = analyze(top100, cap=cap, excluded=excluded)
    print_table(analysis)

    if args.write_docs:
        write_markdown(args.docs_path, source=source, analysis=analysis)
        print(f"Wrote {args.docs_path}", file=sys.stderr)

    # Machine-readable summary line for CI / coordinator paste.
    pct = 100.0 * GROK_FAIR / analysis["theoretical_cap"]
    print(
        json.dumps(
            {
                "theoretical_cap": analysis["theoretical_cap"],
                "n_scoring": analysis["n_scoring"],
                "n_excluded_memo": analysis["n_excluded_memo"],
                "idl_known_cap_upper": analysis["idl_known_cap_upper"],
                "grok_fair": GROK_FAIR,
                "grok_fair_pct_of_cap": round(pct, 4),
                "source": source.get("source"),
                "fetched_at_utc": source.get("fetched_at_utc"),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
