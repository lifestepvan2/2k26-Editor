from __future__ import annotations

from pathlib import Path

import pytest

from nba2k_editor.dead_code import prove_unused as tool


def test_find_symbol_refs_excludes_comments_strings_and_substrings(tmp_path: Path) -> None:
    mod = tmp_path / "mod.py"
    mod.write_text(
        "\n".join(
            [
                "def target_fn():",
                "    return 1",
                "x = target_fn",
                "target_fn()",
                "# target_fn in comment",
                "msg = 'target_fn in string'",
                "target_fn_extra = 5",
            ]
        ),
        encoding="utf-8",
    )

    refs = tool._find_symbol_refs("target_fn", [mod])
    lines = [r["line"] for r in refs]
    assert lines == [1, 3, 4]


def test_callback_ref_edges_are_captured() -> None:
    edges, _callers, callback_callers = tool._build_static_graph(tool.ROOT)
    source = "nba2k_editor.ai.backends.python_backend::generate_async"
    target = "nba2k_editor.ai.backends.python_backend::generate_async._worker"

    assert any(
        e.get("kind") == "callback_ref" and e.get("source") == source and e.get("target") == target
        for e in edges
    )
    assert source in callback_callers.get(target, set())


def test_classification_rules() -> None:
    status, confidence = tool._classify_candidate(
        "orphan",
        {
            "refs_in_runtime": 0,
            "refs_in_tests": 0,
            "static_callers": [],
            "static_callback_callers": [],
        },
        {
            "runtime_hits_total": 0,
            "runtime_hits_in_runtime": 0,
        },
    )
    assert (status, confidence) == ("Proven Unused (High)", "high")

    status, confidence = tool._classify_candidate(
        "test_only_wrapper",
        {
            "refs_in_runtime": 0,
            "refs_in_tests": 2,
            "static_callers": [],
            "static_callback_callers": [],
        },
        {
            "runtime_hits_total": 2,
            "runtime_hits_in_runtime": 0,
        },
    )
    assert (status, confidence) == ("Test-Only Wrapper", "test-only")

    status, confidence = tool._classify_candidate(
        "placeholder",
        {
            "refs_in_runtime": 0,
            "refs_in_tests": 0,
            "static_callers": [],
            "static_callback_callers": [],
        },
        {
            "runtime_hits_total": 0,
            "runtime_hits_in_runtime": 0,
        },
    )
    assert (status, confidence) == ("placeholder", "high")


def test_runtime_instrumentation_preserves_binding_and_exception() -> None:
    class Demo:
        def __init__(self, base: int) -> None:
            self.base = base

        def add(self, value: int) -> int:
            return self.base + value

        def boom(self) -> None:
            raise RuntimeError("boom")

    state: dict[str, dict[str, object]] = {}
    restore_add = tool._instrument_attribute(Demo, "add", "demo::Demo.add", state)
    restore_boom = tool._instrument_attribute(Demo, "boom", "demo::Demo.boom", state)

    try:
        d = Demo(7)
        assert d.add(5) == 12
        assert state["demo::Demo.add"]["runtime_hits_total"] == 1

        with pytest.raises(RuntimeError, match="boom"):
            d.boom()
        assert state["demo::Demo.boom"]["runtime_hits_total"] == 1
    finally:
        restore_boom()
        restore_add()

