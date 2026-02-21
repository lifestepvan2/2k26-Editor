from __future__ import annotations

import sys
import types

import launch_editor


def test_run_child_full_editor_if_requested_routes_arguments(monkeypatch) -> None:
    calls: list[list[str]] = []
    module = types.ModuleType("nba2k_editor.entrypoints.full_editor")
    module.main = lambda args=None: calls.append(list(args or []))  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "nba2k_editor.entrypoints.full_editor", module)

    routed = launch_editor._run_child_full_editor_if_requested(
        ["--child-full-editor", "--editor", "team", "--index", "5"]
    )

    assert routed is True
    assert calls == [["--editor", "team", "--index", "5"]]


def test_run_child_full_editor_if_requested_returns_false_without_flag() -> None:
    routed = launch_editor._run_child_full_editor_if_requested(["--editor", "team", "--index", "5"])

    assert routed is False