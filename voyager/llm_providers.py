"""LLM backends for the code-loop explorer.

Default tests use the fixture provider (no network, no API keys).
OpenRouter/xAI clients are constructed only when those providers are
selected. Grok CLI is optional and never invoked by the offline suite.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any, Sequence

from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage

DEFAULT_FIXTURE_RESPONSE = """I'll start with a simple unsigned sandbox transfer.

```typescript
import { Transaction, SystemProgram, PublicKey } from '@solana/web3.js';

export async function executeSkill(blockhash: string): Promise<string> {
    const tx = new Transaction();
    const agentPubkey = new PublicKey('11111111111111111111111111111111');
    tx.add(
        SystemProgram.transfer({
            fromPubkey: agentPubkey,
            toPubkey: agentPubkey,
            lamports: 1000
        })
    );
    tx.recentBlockhash = blockhash;
    tx.feePayer = agentPubkey;
    return tx.serialize({
        requireAllSignatures: false,
        verifySignatures: false
    }).toString('base64');
}
```
"""

FIXTURE_PROVIDERS = {"fixture", "offline", "dummy"}
GROK_CLI_PROVIDERS = {"grok-cli", "grok_cli", "cli"}


class FixtureLLM:
    """Deterministic canned responses. No network and no API keys."""

    def __init__(
        self,
        responses: Sequence[str] | None = None,
        model_name: str = "fixture",
    ):
        self.responses = list(responses) if responses else [DEFAULT_FIXTURE_RESPONSE]
        self.model_name = model_name
        self.calls = 0

    async def ainvoke(self, messages: Sequence[BaseMessage], **kwargs: Any) -> AIMessage:
        if not self.responses:
            return AIMessage(content="")
        idx = min(self.calls, len(self.responses) - 1)
        self.calls += 1
        return AIMessage(content=self.responses[idx])


class GrokCLILLM:
    """Optional headless Grok CLI backend.

    Invokes ``grok --single`` only when this provider is selected at runtime.
    Offline tests mock subprocess and never call a live model.
    """

    def __init__(
        self,
        model_name: str | None = None,
        grok_bin: str | None = None,
        extra_args: Sequence[str] | None = None,
    ):
        self.model_name = (
            model_name
            or os.getenv("GROK_CLI_MODEL")
            or os.getenv("MODEL_NAME")
            or "grok-4"
        )
        self.grok_bin = grok_bin or os.getenv("GROK_CLI_BIN") or "grok"
        self.extra_args = list(extra_args or [])

    def _format_messages(self, messages: Sequence[BaseMessage]) -> tuple[str | None, str]:
        system_parts: list[str] = []
        user_parts: list[str] = []
        for msg in messages:
            content = getattr(msg, "content", str(msg))
            if isinstance(msg, SystemMessage):
                system_parts.append(content)
            elif isinstance(msg, HumanMessage):
                user_parts.append(content)
            elif isinstance(msg, AIMessage):
                user_parts.append(f"Assistant previously said:\n{content}")
            else:
                user_parts.append(str(content))
        system_prompt = "\n\n".join(system_parts) or None
        prompt = "\n\n".join(user_parts) or (
            "Respond with a TypeScript executeSkill block for a local Solana sandbox."
        )
        return system_prompt, prompt

    @staticmethod
    def parse_cli_output(stdout: str, output_format: str = "plain") -> str:
        text = (stdout or "").strip()
        if output_format != "json":
            return text
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return text
        if isinstance(payload, dict):
            for key in ("text", "content", "response", "output", "message"):
                value = payload.get(key)
                if isinstance(value, str) and value.strip():
                    return value
                if isinstance(value, dict) and isinstance(value.get("content"), str):
                    return value["content"]
            result = payload.get("result")
            if isinstance(result, dict) and isinstance(result.get("content"), str):
                return result["content"]
            if isinstance(result, str) and result.strip():
                return result
        return text

    def build_command(self, prompt: str, system_prompt: str | None) -> list[str]:
        output_format = os.getenv("GROK_CLI_OUTPUT_FORMAT", "plain")
        cmd = [
            self.grok_bin,
            "--single",
            prompt,
            "--output-format",
            output_format,
            "--max-turns",
            "1",
            "--no-subagents",
            "--no-plan",
            "--disable-web-search",
            "--verbatim",
        ]
        if self.model_name:
            cmd.extend(["--model", self.model_name])
        if system_prompt:
            cmd.extend(["--system-prompt-override", system_prompt])
        cmd.extend(self.extra_args)
        return cmd

    async def ainvoke(self, messages: Sequence[BaseMessage], **kwargs: Any) -> AIMessage:
        if shutil.which(self.grok_bin) is None:
            raise FileNotFoundError(
                f"Grok CLI '{self.grok_bin}' not found in PATH. "
                "Install it or set GROK_CLI_BIN. Offline tests use LLM_PROVIDER=fixture."
            )
        system_prompt, prompt = self._format_messages(messages)
        output_format = os.getenv("GROK_CLI_OUTPUT_FORMAT", "plain")
        cmd = self.build_command(prompt, system_prompt)
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            err = (result.stderr or result.stdout or "grok CLI failed").strip()
            raise RuntimeError(f"Grok CLI exited {result.returncode}: {err[:500]}")
        content = self.parse_cli_output(result.stdout, output_format)
        return AIMessage(content=content)


def resolve_provider_name(
    model_name: str | None = None,
    provider: str | None = None,
) -> str:
    explicit = (provider or os.getenv("LLM_PROVIDER") or "").strip().lower()
    model = (model_name or os.getenv("MODEL_NAME") or "").strip().lower()
    if explicit:
        return explicit
    if model in FIXTURE_PROVIDERS:
        return "fixture"
    if model.startswith("grok-cli") or model.startswith("cli/"):
        return "grok-cli"
    if model.startswith("xai/") or model.startswith("grok-"):
        return "xai"
    return "openrouter"


def create_llm(model_name: str, provider: str | None = None):
    """Construct an LLM client. Does not perform any API call."""
    name = resolve_provider_name(model_name, provider)
    if name in FIXTURE_PROVIDERS:
        return FixtureLLM(model_name=model_name)
    if name in GROK_CLI_PROVIDERS:
        return GrokCLILLM(model_name=model_name)
    if name == "xai":
        from langchain_openai import ChatOpenAI

        xai_model = model_name
        if xai_model.startswith("xai/"):
            xai_model = xai_model.split("/", 1)[1]
        return ChatOpenAI(
            base_url=os.getenv("XAI_BASE_URL", "https://api.x.ai/v1"),
            model=xai_model,
            api_key=os.getenv("XAI_API_KEY") or "not-set",
            temperature=0.7,
        )
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        model=model_name,
        api_key=os.getenv("OPENROUTER_API_KEY") or "not-set",
        temperature=0.7,
    )
