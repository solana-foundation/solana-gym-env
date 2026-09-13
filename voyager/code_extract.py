"""Extract TypeScript skill code from model responses. No network I/O."""

from __future__ import annotations

import re
from typing import List, Mapping, Sequence

CODE_BLOCK_PATTERN = re.compile(
    r"```(?:javascript|js|typescript|ts)(.*?)```",
    re.DOTALL,
)

DEFAULT_PROMPT_PATH = "voyager/prompts/basic_system_prompt.txt"

FALLBACK_SYSTEM_PROMPT = """You are exploring Solana in a local sandbox validator.
Your only way to act is TypeScript in ```typescript blocks.
The function signature MUST be:
export async function executeSkill(blockhash: string): Promise<string>
Return a base64-encoded unsigned transaction. Do not submit funded mainnet transactions.
Agent pubkey: {agent_pubkey}
SOL balance: {sol_balance}
Block height: {block_height}
Total reward: {total_reward}
Message budget: {max_messages}
"""


def extract_code_blocks(message_content: str) -> List[str]:
    """Return non-empty TypeScript/JavaScript fenced code blocks."""
    if not message_content:
        return []
    blocks = CODE_BLOCK_PATTERN.findall(message_content)
    return [block.strip() for block in blocks if block.strip()]


def create_skill_code(code_blocks: Sequence[str]) -> str:
    """Prefer a block that exports executeSkill; otherwise the first block."""
    if not code_blocks:
        return ""
    for block in code_blocks:
        if "export async function executeSkill" in block:
            return block.strip()
    return code_blocks[0].strip()


def render_system_prompt(
    template: str,
    *,
    agent_pubkey: str = "",
    sol_balance: float = 0,
    block_height: int = 0,
    total_reward: float = 0,
    max_messages: int = 0,
) -> str:
    return template.format(
        agent_pubkey=agent_pubkey,
        sol_balance=sol_balance,
        block_height=block_height,
        total_reward=total_reward,
        max_messages=max_messages,
    )


def load_system_prompt_template(
    env_config: Mapping[str, object] | None = None,
    *,
    default_path: str = DEFAULT_PROMPT_PATH,
) -> str:
    """Load the env prompt template, then the basic prompt, then a fallback."""
    candidates: list[str] = []
    if env_config:
        configured = env_config.get("system_prompt_template")
        if isinstance(configured, str) and configured:
            candidates.append(configured)
    candidates.append(default_path)
    for path in candidates:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return handle.read()
        except OSError:
            continue
    return FALLBACK_SYSTEM_PROMPT
