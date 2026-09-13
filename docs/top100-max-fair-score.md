# Top-100 max fair score estimate

## Verdict

| Metric | Value |
|--------|------:|
| **theoretical_cap** (`32 × N`) | **3136** |
| N (top-100 minus Memo v1/v2) | 98 |
| Memo excluded from top-100 | 2 |
| Per-program cap | 32 |
| idl_known_cap (upper; unknowns@cap) | 3014 |
| idl_known_only (sum over cataloged) | 102 (7 programs) |
| Grok fair / raw | **66** / 70 |
| **Grok fair ÷ theoretical_cap** | **2.10%** |

## Method

Fair scoring reuses `voyager/scoring.py`:

- `+1` per unique `(program_id, first_byte_of_ix_data)` on successful txs
- Memo v1/v2 in `DEFAULT_EXCLUDED_PROGRAMS` → fair contribution **0**
- Cap `max_unique_per_program=32` (`SCORE_MAX_UNIQUE_PER_PROGRAM`)
- Zero-account spam-shaped ixs do not score when metas are present
- Per-program fair ceiling = `min(32, distinct_first_bytes_that_can_succeed)`
- **First-pass ceiling** assumes saturating the cap → `theoretical_cap = 32 × (# non-Memo programs in top 100)`

No Memo farms. Rankings are **not invented**.

## Source

- **kind:** `solana_rpc_getBlock_sample`
- **detail:** Public Solana RPC getBlock sampling of recent mainnet blocks. Ranked by successful transactions that invoke the program (top-level + inner instructions). Not invented rankings.
- **fetched_at_utc:** `2026-09-13T21:36:27.527789+00:00`
- **rpc:** `https://api.mainnet-beta.solana.com`
- **blocks_sampled:** 80
- **slot range:** 446806582 … 446806977 (tip at start `446806987`)
- **metric:** `successful_tx_count_containing_program` (secondary `instruction_invocation_count`)

Refresh:

```bash
PYTHONPATH=. python3 scripts/top100_max_fair_score.py --refresh --write-docs
# or use the checked-in snapshot only:
PYTHONPATH=. python3 scripts/top100_max_fair_score.py --snapshot docs/top100_programs_snapshot.json --write-docs
```

Checked-in snapshot: [`docs/top100_programs_snapshot.json`](./top100_programs_snapshot.json).

If live RPC refresh fails (rate limits / network), keep using the snapshot JSON;
do not invent a ranking.

## Comparison to Grok fair climb

Canonical Grok fair climb: fair **66** / raw **70** / memo **0**.

Against this top-100 first-pass ceiling (**3136**), Grok reached **2.10%** of the saturating theoretical max. That ceiling is an **upper bound** (many programs cannot expose 32 distinct successful first-bytes; Anchor discriminators also collide on byte0).

## Per-program table (top 100 by usage)

| rank | program_id | name | tx_count | fair_ceiling_32 | idl_known_cap | notes |
|-----:|------------|------|---------:|----------------:|--------------:|-------|
| 1 | `Vote111111111111111111111111111111111111111` | Vote Program | 53970 | 32 | 16 | known_first_bytes=16 |
| 2 | `ComputeBudget111111111111111111111111111111` | Compute Budget | 23817 | 32 | 5 | known_first_bytes=5 |
| 3 | `11111111111111111111111111111111` | System Program | 15596 | 32 | 13 | known_first_bytes=13 |
| 4 | `TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA` | SPL Token | 12143 | 32 | 28 | known_first_bytes=28 |
| 5 | `ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL` | Associated Token Account | 10212 | 32 | 3 | known_first_bytes=3 |
| 6 | `TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb` | Token-2022 | 9247 | 32 | 32 | known_first_bytes=48 |
| 7 | `pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ` | Pump Fees | 7902 | 32 | — | unknown ix catalog → assume cap |
| 8 | `pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA` | Pump AMM | 7058 | 32 | — | unknown ix catalog → assume cap |
| 9 | `cpamdpZCGKUy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG` | Meteora DAMM v2 | 1722 | 32 | — | unknown ix catalog → assume cap |
| 10 | `QuaNtZsgYRe5Z9Bk4LZ4cTD9tbkVoyCNf1R2BN9bBDv` | — | 1320 | 32 | — | unknown ix catalog → assume cap |
| 11 | `EtrnLzgbS7nMMy5fbD42kXiUzGg8XQzJ972Xtk1cjWih` | — | 1062 | 32 | — | unknown ix catalog → assume cap |
| 12 | `6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P` | pump.fun | 996 | 32 | — | unknown ix catalog → assume cap |
| 13 | `9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp` | — | 980 | 32 | — | unknown ix catalog → assume cap |
| 14 | `TessVdML9pBGgG9yGks7o4HewRaXVAMuoVj4x83GLQH` | TesseraV | 945 | 32 | — | unknown ix catalog → assume cap |
| 15 | `JUP6LkbZbjS1jK/wapdHNy74zcZ3tLUZoi5QNyVTaV4` | — | 740 | 32 | — | unknown ix catalog → assume cap |
| 16 | `HVi6VyyLvTtFTA8f8atavxVjUKi8WjmnydfKgoZKzt7H` | — | 698 | 32 | — | unknown ix catalog → assume cap |
| 17 | `MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr` | Memo v2 | 608 | 0 | — | excluded (Memo) |
| 18 | `FLASHX8DrLbgeR8FcfNV1F5krxYcYMUdBkrP1EPBtxB9` | Flash Loan Aggregator | 538 | 32 | — | unknown ix catalog → assume cap |
| 19 | `BiSoNHVpsVZW2F7rx2eQ59yQwKxzU5NvBcmKshCSUypi` | — | 521 | 32 | — | unknown ix catalog → assume cap |
| 20 | `CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK` | Raydium CLMM | 514 | 32 | — | unknown ix catalog → assume cap |
| 21 | `FsU1rcaEC361jBr9JE5wm7bpWRSTYeAMN4R2MCs11rNF` | — | 512 | 32 | — | unknown ix catalog → assume cap |
| 22 | `3QUnrcMqCQoiGB73s1A6uDzxziywaNFpTLiZiiZbEUoN` | — | 492 | 32 | — | unknown ix catalog → assume cap |
| 23 | `9L1qqo7q7vq7sKuMsBGKPF81z6GK7N4orWGgGFwwqqDF` | — | 487 | 32 | — | unknown ix catalog → assume cap |
| 24 | `LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo` | Meteora DLMM | 469 | 32 | — | unknown ix catalog → assume cap |
| 25 | `BPFLoaderUpgradeab1e11111111111111111111111` | BPF Upgradeable Loader | 436 | 32 | — | unknown ix catalog → assume cap |
| 26 | `DF1ow4tspfHX9JwWJsAb9epbkA8hmpSEAtxXy1V27QBH` | — | 430 | 32 | — | unknown ix catalog → assume cap |
| 27 | `W1LDCARDa67SPBG7TFpQivHnEZXRtxCFP13ysEd1bWR` | — | 423 | 32 | — | unknown ix catalog → assume cap |
| 28 | `FLUX6xBayGxLX9UcimVRxXFMHH6q43mAbRvDzSpCsvfK` | — | 398 | 32 | — | unknown ix catalog → assume cap |
| 29 | `Archer8kgiavM61GyusMzaaS2ft5sALtNsD1HxkUPMhy` | — | 391 | 32 | — | unknown ix catalog → assume cap |
| 30 | `CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C` | Raydium CPMM | 389 | 32 | — | unknown ix catalog → assume cap |
| 31 | `ojh19ojaKduoJZuaJADhcVGp4xt1TcdAvZmpVsCorch` | — | 382 | 32 | — | unknown ix catalog → assume cap |
| 32 | `dijkbkCAKfFTCxQg3u1pg82gVU1jJGHBBRcteD11mBu` | — | 367 | 32 | — | unknown ix catalog → assume cap |
| 33 | `dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN` | Dynamic Bonding Curve | 350 | 32 | — | unknown ix catalog → assume cap |
| 34 | `BYdq7NJXWHnTzzCogT6VByrPXvUQwkD5PuZQLS8JvZtw` | — | 324 | 32 | — | unknown ix catalog → assume cap |
| 35 | `whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc` | Orca Whirlpool | 264 | 32 | — | unknown ix catalog → assume cap |
| 36 | `675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8` | Raydium AMM v4 | 257 | 32 | — | unknown ix catalog → assume cap |
| 37 | `7kE7pY98M9hqdYjjEk6dHH7KGu6TESWfN4DWxZ1UirRu` | — | 251 | 32 | — | unknown ix catalog → assume cap |
| 38 | `MAyhSmzXzV1pTf7LsNkrNwkWKTo4ougAJ1PPg47MD4e` | — | 208 | 32 | — | unknown ix catalog → assume cap |
| 39 | `DZNTS5ujuiyx1mazqCPdYPzEyE2VrTPPb6QbqBUftJbY` | — | 206 | 32 | — | unknown ix catalog → assume cap |
| 40 | `tickUcsEQegChaAuo9VYQQztB4ZGApY6ZT4FkULWY6N` | — | 200 | 32 | — | unknown ix catalog → assume cap |
| 41 | `SAGE2HAwep459SNq61LHvjxPk4pLPEJLoMETef7f7EE` | — | 199 | 32 | — | unknown ix catalog → assume cap |
| 42 | `B72M6nyCLFgWiJtAN4naUTminMiTmyGcEqQHXwVeRdht` | — | 189 | 32 | — | unknown ix catalog → assume cap |
| 43 | `proVF4pMXVaYqmy4NjniPh4pqKNfMmsihgd4wdkCX3u` | — | 179 | 32 | — | unknown ix catalog → assume cap |
| 44 | `REALQqNEomY6cQGZJUGwywTBD2UmDT32rZcNnfxQ5N2` | — | 150 | 32 | — | unknown ix catalog → assume cap |
| 45 | `HRHjd1NCXLAvCTQERXTyTKUWUqcLGaRHKwLwGmUZ9cJq` | — | 149 | 32 | — | unknown ix catalog → assume cap |
| 46 | `Tri3NG4HkZ6DddYPKoX2ehgkqFtDuej9Aspw5BmvSo4` | — | 149 | 32 | — | unknown ix catalog → assume cap |
| 47 | `orafZ4BdfzikRRg498P23vG3EdEyMR7bYoYcD2zcwiD` | — | 146 | 32 | — | unknown ix catalog → assume cap |
| 48 | `6Vo3245eszAb5wuqEMw8mGdbfRUdKbHhDHP5LcaGuTAB` | — | 140 | 32 | — | unknown ix catalog → assume cap |
| 49 | `idemJL67fKhpev5vKcxHrosuVyTat6wVC9sFfoPVg3Y` | — | 134 | 32 | — | unknown ix catalog → assume cap |
| 50 | `LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj` | Raydium LaunchLab | 128 | 32 | — | unknown ix catalog → assume cap |
| 51 | `Hd7c1kYHqYJ7dD1bLf9C61XC22JgbGp4P1PQ8UNcUH5w` | — | 119 | 32 | — | unknown ix catalog → assume cap |
| 52 | `Cargo2VNTPPTi9c1vq1Jw5d3BWUNr18MjRtSupAghKEk` | — | 112 | 32 | — | unknown ix catalog → assume cap |
| 53 | `7q9uKyKWW5ddfyRiaJzFeKZTCMVToHhyZJ5sAPKK174L` | — | 110 | 32 | — | unknown ix catalog → assume cap |
| 54 | `FD1amxhTsDpwzoVX41dxp2ygAESURV2zdUACzxM1Dfw9` | — | 106 | 32 | — | unknown ix catalog → assume cap |
| 55 | `term9YPb9mzAsABaqN71A4xdbxHmpBNZavpBiQKZzN3` | — | 105 | 32 | — | unknown ix catalog → assume cap |
| 56 | `99vQwtBwYtrqqD9YSXbdum3KBdxPAVxYTaQ3cfnJSrN2` | — | 104 | 32 | — | unknown ix catalog → assume cap |
| 57 | `MNFSTqtC93rEfYHB6hF82sKdZpUDFWkViLByLd1k1Ms` | — | 102 | 32 | — | unknown ix catalog → assume cap |
| 58 | `phDEVv4w6BcfkLrLNeXr8HhhgQxnxziVGXpGPcaadMf` | — | 96 | 32 | — | unknown ix catalog → assume cap |
| 59 | `FW6zUqn4iKRaeopwwhwsquTY6ABWLLgjxtrC3VPnaWBf` | — | 94 | 32 | — | unknown ix catalog → assume cap |
| 60 | `FoaFt2Dtz58RA6DPjbRb9t9z8sLJRChiGFTv21EfaseZ` | — | 94 | 32 | — | unknown ix catalog → assume cap |
| 61 | `ALPHAQmeA7bjrVuccPsYPiCvsi428SNwte66Srvs4pHA` | — | 89 | 32 | — | unknown ix catalog → assume cap |
| 62 | `Point2iBvz7j5TMVef8nEgpmz4pDr7tU7v3RjAfkQbM` | — | 89 | 32 | — | unknown ix catalog → assume cap |
| 63 | `AyqnbctmwCvd3fpgddrBaWWgkMFuiVCUXWU83WGvSJLt` | — | 85 | 32 | — | unknown ix catalog → assume cap |
| 64 | `Ed25519SigVerify111111111111111111111111111` | Ed25519 SigVerify | 74 | 32 | — | unknown ix catalog → assume cap |
| 65 | `Ax8aVosP3b55aZu3FRD3m4JCrvHBWzAkkoV4yBCWHdY1` | — | 72 | 32 | — | unknown ix catalog → assume cap |
| 66 | `3TK9D8aoBFYjYZtKCjciPrVrRStsnvo7KmpcJqDavpaU` | — | 69 | 32 | — | unknown ix catalog → assume cap |
| 67 | `AjMx5My4YUDHMiCtLpTAtgkiUJgrpJnQqd5AcQnddHQW` | — | 69 | 32 | — | unknown ix catalog → assume cap |
| 68 | `HFn8GnPADiny6XqUoWE8uRPPxb29ikn4yTuPa9MF2fWJ` | — | 68 | 32 | — | unknown ix catalog → assume cap |
| 69 | `HDwcJBJXjL9FpJ7UBsYBtaDjsBUhuLCUYoz3zr8SWWaQ` | — | 66 | 32 | — | unknown ix catalog → assume cap |
| 70 | `rec5EKMGg6MxZYaMdyBfgwp4d5rB9T1VQH5pJv5LtFJ` | Pyth Receiver | 66 | 32 | — | unknown ix catalog → assume cap |
| 71 | `hydHwdP54fiTbJ5QXuKDLZFLY5m8pqx15RSmWcL1yAJ` | — | 64 | 32 | — | unknown ix catalog → assume cap |
| 72 | `GMGNreQcJFufBiCTLDBgKhYEfEe9B454UjpDr5CaSLA1` | — | 63 | 32 | — | unknown ix catalog → assume cap |
| 73 | `pythWSnswVUd12oZpeFP8e9CVaEqJg25g1Vtc2biRsT` | Pyth Oracle | 63 | 32 | — | unknown ix catalog → assume cap |
| 74 | `mmm3XBJg5gk8XJxEKBvdgptZz6SgK4tXvn36sodowMc` | MPL Magic Eden MMM | 61 | 32 | — | unknown ix catalog → assume cap |
| 75 | `E2uCGJ4TtYyKPGaK57UMfbs9sgaumwDEZF1aAY6fF3mS` | — | 60 | 32 | — | unknown ix catalog → assume cap |
| 76 | `HiPMPcYjLNPgjvdzBoavzMbCeHaXWkAuDxyuE9VoPrkf` | — | 59 | 32 | — | unknown ix catalog → assume cap |
| 77 | `4bwVxjN2sFQyejtoa9ieiD1rRpPY798QGTKVDcmnotWu` | — | 56 | 32 | — | unknown ix catalog → assume cap |
| 78 | `vELoC1audYbSYVRXn1vPaV8Axoa9oU6BYmNGZZBDZ1P` | — | 55 | 32 | — | unknown ix catalog → assume cap |
| 79 | `L2TExMFKdjpN9kozasaurPirfHy9P8sbXoAN1qA3S95` | Lighthouse | 54 | 32 | — | unknown ix catalog → assume cap |
| 80 | `2DNbzPochEcyCcWMbL4d9S3u9QqQEj5bbe6cSZFvKsbh` | — | 53 | 32 | — | unknown ix catalog → assume cap |
| 81 | `DhpyNWkdxFh3DRPsBrwRwrK3TYC5t7Q4arnSvf3t84HY` | — | 52 | 32 | — | unknown ix catalog → assume cap |
| 82 | `goonuddtQRrWqqn5nFyczVKaie28f3kDkHWkHtURSLE` | — | 50 | 32 | — | unknown ix catalog → assume cap |
| 83 | `ExA6GYhHAeRNMWVNLrDir1SKPJZcZA2oaPq6uriSmxfJ` | — | 48 | 32 | — | unknown ix catalog → assume cap |
| 84 | `AddressLookupTab1e1111111111111111111111111` | Address Lookup Table | 44 | 32 | 5 | known_first_bytes=5 |
| 85 | `Gt9S41PtjR58CbG9JhJ3J6vxesqrNAswbWYbLNTMZA3c` | — | 38 | 32 | — | unknown ix catalog → assume cap |
| 86 | `T1TANpTeScyeqVzzgNViGDNrkQ6qHz9KrSBS4aNXvGT` | — | 36 | 32 | — | unknown ix catalog → assume cap |
| 87 | `pyt2F414BA6dPttK6RddPZUdHfapoBN24GL5wbrPCou` | — | 36 | 32 | — | unknown ix catalog → assume cap |
| 88 | `rec2HHDDnjLfj4kE7VyEtFA1HPGQLK33259532cRyHp` | — | 36 | 32 | — | unknown ix catalog → assume cap |
| 89 | `TCMPhJdwDryooaGtiocG1u3xcYbRpiJzb283XfCZsDp` | — | 35 | 32 | — | unknown ix catalog → assume cap |
| 90 | `DNL1tgEj3nJovHw9jtyCCQD3arssCJzkmpDizknwzey4` | — | 33 | 32 | — | unknown ix catalog → assume cap |
| 91 | `FarmsPZpWu9i7Kky8tPN37rs2TpmMrAZrC7S7vJa91Hr` | — | 33 | 32 | — | unknown ix catalog → assume cap |
| 92 | `BoobsBSMpFRBA91sNwKLYShRRQPH5GjoCH4NhLUt4yRo` | — | 31 | 32 | — | unknown ix catalog → assume cap |
| 93 | `HDw2E7P8X1SkCyjvoGsfBGAVUutKcj874bXjHrpVYrVL` | — | 31 | 32 | — | unknown ix catalog → assume cap |
| 94 | `HpNfyc2Saw7RKkQd8nEL4khUcuPhQ7WwY1B2qjx8jxFq` | — | 30 | 32 | — | unknown ix catalog → assume cap |
| 95 | `satRushGBRY2vgapeTAkoxz26vL2cYqyPi6CnBj7Tco` | — | 30 | 32 | — | unknown ix catalog → assume cap |
| 96 | `2gLMrDm6b3hCxY7UfDUERe3pmuhHWwReJ8AreVyGEF7o` | — | 29 | 32 | — | unknown ix catalog → assume cap |
| 97 | `BopTVfs428fBBX2vf28FgdAjzX5F8vAhsaG3SrCs4rHm` | — | 28 | 32 | — | unknown ix catalog → assume cap |
| 98 | `prediCtPZCttYMvm2W3PtxmMxLmT1dtN7riU6Cxh6tM` | — | 28 | 32 | — | unknown ix catalog → assume cap |
| 99 | `Memo1UhkJRfHyvLMcVucJwxXeuD728EqVDDwQDxFMNo` | Memo v1 | 26 | 0 | — | excluded (Memo) |
| 100 | `ForaPmWWcahJbcnUXM1JJKfzntvAsACddY4rm85wtt4j` | — | 25 | 32 | — | unknown ix catalog → assume cap |

## Notes on `idl_known_cap`

Cataloged counts come from public native/SPL instruction enums (System, Vote, Stake, ComputeBudget, ALT, Token, Token-2022, ATA) where the first data byte is the instruction tag. Token-2022 has >32 tags → capped at 32. Programs without a catalog still count as **32** in `idl_known_cap_upper` so that figure remains an upper bound, not a tight IDL sum. `idl_known_only` is the sum over cataloged programs alone.

