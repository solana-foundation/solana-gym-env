from voyager.code_extract import (
    FALLBACK_SYSTEM_PROMPT,
    create_skill_code,
    extract_code_blocks,
    load_system_prompt_template,
    render_system_prompt,
)


def test_extract_typescript_and_js_blocks():
    message = """
Try this first.
```typescript
export async function executeSkill(blockhash: string): Promise<string> {
  return "aaa";
}
```
And JS:
```js
const x = 1;
```
"""
    blocks = extract_code_blocks(message)
    assert len(blocks) == 2
    assert "executeSkill" in blocks[0]
    assert "const x = 1;" in blocks[1]


def test_extract_empty_and_non_code():
    assert extract_code_blocks("") == []
    assert extract_code_blocks("no fences here") == []


def test_create_skill_code_prefers_execute_skill():
    blocks = [
        "const leftover = true;",
        "export async function executeSkill(blockhash: string): Promise<string> { return 'tx'; }",
    ]
    skill = create_skill_code(blocks)
    assert "executeSkill" in skill
    assert create_skill_code([]) == ""
    assert create_skill_code(["only one"]) == "only one"


def test_render_and_fallback_prompt(tmp_path):
    rendered = render_system_prompt(
        FALLBACK_SYSTEM_PROMPT,
        agent_pubkey="Abc",
        sol_balance=1.5,
        block_height=9,
        total_reward=3,
        max_messages=4,
    )
    assert "Abc" in rendered
    assert "1.5" in rendered
    assert "4" in rendered

    missing = load_system_prompt_template(
        {"system_prompt_template": str(tmp_path / "nope.txt")},
        default_path=str(tmp_path / "also-missing.txt"),
    )
    assert "executeSkill" in missing
