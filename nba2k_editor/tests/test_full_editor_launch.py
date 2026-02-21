from __future__ import annotations

import sys

from nba2k_editor.ui.full_editor_launch import build_launch_command


def test_build_launch_command_source_mode(monkeypatch) -> None:
    monkeypatch.delattr(sys, "frozen", raising=False)

    cmd = build_launch_command(editor="team", index=5)

    assert cmd[:3] == [sys.executable, "-m", "nba2k_editor.entrypoints.full_editor"]
    assert cmd[-4:] == ["--editor", "team", "--index", "5"]


def test_build_launch_command_frozen_mode(monkeypatch) -> None:
    monkeypatch.setattr(sys, "frozen", True, raising=False)

    cmd = build_launch_command(editor="staff", index=12)

    assert cmd[:2] == [sys.executable, "--child-full-editor"]
    assert cmd[-4:] == ["--editor", "staff", "--index", "12"]


def test_build_launch_command_player_indices_deduplicated() -> None:
    cmd = build_launch_command(editor="player", indices=[4, 4, 9, -1, 2])

    assert cmd[-4:] == ["--editor", "player", "--indices", "4,9,2"]