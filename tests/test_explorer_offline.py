"""Offline explorer plumbing tests. No validator, no paid APIs."""

import asyncio
from types import SimpleNamespace

import pytest

from voyager.code_extract import load_system_prompt_template, render_system_prompt
from voyager.llm_providers import FixtureLLM


class FakeEnv:
    def __init__(self):
        self.agent_keypair = SimpleNamespace(pubkey=lambda: "Agent111111111111111111111111111111")
        self.total_reward = 0
        self.client = SimpleNamespace(get_latest_blockhash=self._blockhash)
        self.steps = []

    async def _get_observation(self, last_tx_result=None):
        return [["observe", {"sol_balance": 2.0, "block_height": 10}]]

    async def _blockhash(self):
        return SimpleNamespace(value=SimpleNamespace(blockhash="Blockhash111"))

    def _partial_sign_transaction(self, tx_bytes, signers):
        return {"signed": True, "bytes": tx_bytes}

    async def step(self, tx):
        self.steps.append(tx)
        self.total_reward += 1
        info = {
            "programs_interacted": ["11111111111111111111111111111111"],
            "unique_instructions": {"11111111111111111111111111111111": [2]},
            "reward": 1,
        }
        obs = await self._get_observation()
        return obs, 1, False, False, info


def _make_explorer(tmp_path, llm):
    pytest.importorskip("solders")
    pytest.importorskip("gymnasium")
    try:
        from code_loop_explorer import CodeLoopExplorer
    except ImportError as exc:
        pytest.skip(f"code_loop_explorer import requires sandbox extras: {exc}")

    return CodeLoopExplorer(
        model_name="fixture",
        max_messages=2,
        checkpoint_dir=str(tmp_path / "ckpt"),
        environment_config="voyager/environments/basic_env.json",
        llm=llm,
        llm_provider="fixture",
        metrics_dir=str(tmp_path / "metrics"),
        verbose=False,
    )


def test_system_prompt_without_env_config():
    template = load_system_prompt_template(None)
    prompt = render_system_prompt(
        template,
        agent_pubkey="Agent111",
        sol_balance=2,
        block_height=1,
        total_reward=0,
        max_messages=3,
    )
    assert "Agent111" in prompt
    assert "executeSkill" in prompt


def test_timeout_defaults_when_env_config_missing(tmp_path):
    explorer = _make_explorer(tmp_path, FixtureLLM())
    explorer.env_config = None
    assert explorer._skill_timeout_ms() == 30000
    explorer.env_config = {"timeout": 4000}
    assert explorer._skill_timeout_ms() == 4000


def test_loop_handles_missing_code_blocks(tmp_path):
    explorer = _make_explorer(tmp_path, FixtureLLM(responses=["no code here"]))
    env = FakeEnv()
    explorer.max_messages = 1
    asyncio.run(explorer.run_exploration_loop(env))
    assert explorer.message_count == 1
    metrics = explorer.metrics["messages"][0]
    assert metrics["reward"] == 0
    assert metrics["instructions_discovered"] == {}
    assert metrics["code_extracted"] is False


def test_loop_executes_fixture_code_without_rpc(tmp_path):
    explorer = _make_explorer(tmp_path, FixtureLLM())
    env = FakeEnv()
    explorer.max_messages = 1

    def fake_run_code(code, pubkey, blockhash, code_file, timeout):
        assert "executeSkill" in code
        assert timeout == 4000
        return {"serialized_tx": "AAAA", "success": True}

    explorer.skill_manager.run_code_loop_code = fake_run_code
    asyncio.run(explorer.run_exploration_loop(env))
    assert env.steps
    assert explorer.metrics["messages"][0]["reward"] == 1
    assert "11111111111111111111111111111111" in explorer.metrics["programs_discovered"]
    saved = list((tmp_path / "metrics").glob("*_metrics.json"))
    assert saved
