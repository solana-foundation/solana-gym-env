from voyager.metrics_summary import summarize_code_loop_run


def test_success_rate_uses_code_blocks_extracted():
    metrics = {
        "code_blocks_extracted": [
            {"success": True, "reward": 2},
            {"success": False, "reward": 0},
        ],
        "messages": [
            {"reward": 2, "code_extracted": True},
            {"reward": 0, "code_extracted": True},
        ],
        "programs_discovered": {"11111111111111111111111111111111": 1},
        "instructions_by_program": {"11111111111111111111111111111111": [2]},
    }
    summary = summarize_code_loop_run(metrics)
    assert summary["successful_blocks"] == 1
    assert summary["total_blocks"] == 2
    assert summary["success_rate"] == 0.5
    assert summary["unique_instructions"] == 1
    assert summary["programs_discovered"] == 1


def test_legacy_metrics_without_code_extracted_flag():
    metrics = {
        "messages": [
            {"reward": 3, "instructions_discovered": {"MemoSq4": [0, 1]}},
            {"reward": 0, "instructions_discovered": {}},
        ],
        "programs_discovered": {},
        "instructions_by_program": {},
    }
    summary = summarize_code_loop_run(metrics)
    assert summary["successful_blocks"] == 1
    assert summary["total_blocks"] == 2
    assert summary["success_rate"] == 0.5
    assert summary["unique_instructions"] == 2
