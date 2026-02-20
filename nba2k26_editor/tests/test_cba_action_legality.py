from __future__ import annotations

from pathlib import Path

import pytest

from gm_rl.actions import ActionMaskBuilder, ActionSpaceSpec
from gm_rl.adapters.local_mock import LocalMockAdapter
from nba2k_editor.gm_rl.cba.extractors import extract_raw_rules, load_manifest, load_manual_overrides
from nba2k_editor.gm_rl.cba.normalizer import normalize_rules


pytest.importorskip("docx")


def _ruleset():
    source = Path(__file__).resolve().parents[1] / "CBA" / "2023-NBA-Collective-Bargaining-Agreement.docx"
    manifest = load_manifest()
    overrides = load_manual_overrides()
    raw, citations = extract_raw_rules(source, manifest=manifest)
    ruleset, _ = normalize_rules(raw, citations, season="2025-26", manifest=manifest, overrides=overrides)
    return ruleset


def test_cba_blocks_trade_after_deadline_and_emits_warning():
    adapter = LocalMockAdapter(seed=9)
    state = adapter.load_roster_state(seed=9)
    state.context.current_week = state.context.trade_deadline_week
    builder = ActionMaskBuilder(ActionSpaceSpec(), cba_rules=_ruleset())
    mask = builder.build(state, team_id=1)
    assert not mask.trade.any()
    assert "cba_blocked_trade_deadline" in builder.last_cba_block_reasons
    assert "cba_warn_trade_wait_windows_unchecked" in builder.last_cba_warn_reasons


def test_cba_blocks_contracts_when_hard_cap_reached():
    adapter = LocalMockAdapter(seed=10)
    state = adapter.load_roster_state(seed=10)
    team = state.get_team(1)
    team.payroll = state.context.hard_cap + 1.0
    builder = ActionMaskBuilder(ActionSpaceSpec(), cba_rules=_ruleset())
    mask = builder.build(state, team_id=1)
    assert not mask.contract.any()
    assert "cba_blocked_hard_cap_contract" in builder.last_cba_block_reasons

