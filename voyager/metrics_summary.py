"""Summarize code-loop metric files without plotting dependencies."""

from __future__ import annotations


def summarize_code_loop_run(metrics: dict) -> dict:
    """Summarize one run using fields the explorer actually writes."""
    extracted = metrics.get("code_blocks_extracted") or []
    messages = metrics.get("messages") or []
    if extracted:
        successful_blocks = sum(
            1 for block in extracted if block.get("success") or block.get("reward", 0) > 0
        )
        total_blocks = len(extracted)
    else:
        successful_blocks = sum(1 for msg in messages if msg.get("reward", 0) > 0)
        coded = [msg for msg in messages if msg.get("code_extracted")]
        total_blocks = len(coded) if coded else len(messages)

    success_rate = successful_blocks / total_blocks if total_blocks else 0
    programs = len(metrics.get("programs_discovered") or {})
    instructions = sum(
        len(instr_list)
        for instr_list in (metrics.get("instructions_by_program") or {}).values()
    )
    if instructions == 0:
        seen_ix = set()
        for msg in messages:
            discovered = msg.get("instructions_discovered") or {}
            if isinstance(discovered, dict):
                for prog_id, discs in discovered.items():
                    values = discs if isinstance(discs, (list, set, tuple)) else [discs]
                    for disc in values:
                        seen_ix.add((prog_id, disc))
        instructions = len(seen_ix)
    return {
        "successful_blocks": successful_blocks,
        "total_blocks": total_blocks,
        "success_rate": success_rate,
        "programs_discovered": programs,
        "unique_instructions": instructions,
    }
