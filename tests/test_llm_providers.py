import asyncio
import json
from types import SimpleNamespace

import pytest
from langchain.schema import AIMessage, HumanMessage, SystemMessage

from voyager.llm_providers import (
    FixtureLLM,
    GrokCLILLM,
    create_llm,
    resolve_provider_name,
)


def test_fixture_llm_is_deterministic():
    llm = FixtureLLM(responses=["first", "second"])

    async def run():
        first = await llm.ainvoke([HumanMessage(content="go")])
        second = await llm.ainvoke([HumanMessage(content="again")])
        third = await llm.ainvoke([HumanMessage(content="again")])
        return first, second, third

    first, second, third = asyncio.run(run())
    assert first.content == "first"
    assert second.content == "second"
    assert third.content == "second"
    assert "executeSkill" in FixtureLLM().responses[0]


def test_resolve_provider_name(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("MODEL_NAME", raising=False)
    assert resolve_provider_name("fixture") == "fixture"
    assert resolve_provider_name("grok-4") == "xai"
    assert resolve_provider_name("xai/grok-3") == "xai"
    assert resolve_provider_name("google/gemini-2.5-flash") == "openrouter"
    monkeypatch.setenv("LLM_PROVIDER", "grok-cli")
    assert resolve_provider_name("anything") == "grok-cli"


def test_create_llm_fixture_does_not_need_keys(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fixture")
    llm = create_llm("ignored")
    assert isinstance(llm, FixtureLLM)


def test_grok_cli_parses_json_and_plain():
    assert GrokCLILLM.parse_cli_output("hello", "plain") == "hello"
    payload = json.dumps({"content": "```typescript\ncode\n```"})
    assert "typescript" in GrokCLILLM.parse_cli_output(payload, "json")


def test_grok_cli_build_command_is_headless():
    client = GrokCLILLM(model_name="grok-4", grok_bin="grok")
    cmd = client.build_command("write a skill", "system text")
    assert cmd[0] == "grok"
    assert "--single" in cmd
    assert "--no-subagents" in cmd
    assert "--disable-web-search" in cmd
    assert "grok-4" in cmd


def test_grok_cli_missing_binary(monkeypatch):
    monkeypatch.setattr("voyager.llm_providers.shutil.which", lambda _: None)
    client = GrokCLILLM(grok_bin="grok-not-installed")
    with pytest.raises(FileNotFoundError):
        asyncio.run(client.ainvoke([HumanMessage(content="hi")]))


def test_grok_cli_mocked_subprocess(monkeypatch):
    monkeypatch.setattr("voyager.llm_providers.shutil.which", lambda _: "/usr/bin/grok")

    def fake_run(cmd, capture_output, text, check):
        assert cmd[0] == "grok"
        assert "--single" in cmd
        return SimpleNamespace(
            returncode=0,
            stdout="```ts\nexport async function executeSkill(){}\n```",
            stderr="",
        )

    monkeypatch.setattr("voyager.llm_providers.subprocess.run", fake_run)
    client = GrokCLILLM(model_name="grok-4")
    result = asyncio.run(
        client.ainvoke(
            [SystemMessage(content="sandbox only"), HumanMessage(content="go")]
        )
    )
    assert isinstance(result, AIMessage)
    assert "executeSkill" in result.content
