from __future__ import annotations

import importlib


def test_gm_rl_alias_points_to_integrated_package():
    legacy = importlib.import_module("gm_rl.actions")
    integrated = importlib.import_module("nba2k_editor.gm_rl.actions")
    assert legacy.__file__ == integrated.__file__

