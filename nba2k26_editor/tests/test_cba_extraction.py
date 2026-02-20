from __future__ import annotations

from pathlib import Path

import pytest

from nba2k_editor.gm_rl.cba.extractors import extract_raw_rules, load_manifest, load_manual_overrides
from nba2k_editor.gm_rl.cba.normalizer import normalize_rules


pytest.importorskip("docx")


def _source_doc() -> Path:
    return Path(__file__).resolve().parents[1] / "CBA" / "2023-NBA-Collective-Bargaining-Agreement.docx"


def test_cba_extraction_core_constants_and_tables():
    manifest = load_manifest()
    overrides = load_manual_overrides()
    raw, citations = extract_raw_rules(_source_doc(), manifest=manifest)
    ruleset, report = normalize_rules(
        raw,
        citations,
        season="2025-26",
        manifest=manifest,
        overrides=overrides,
    )

    assert ruleset.cap.first_apron_by_season["2025-26"] == 187_500_000.0
    assert ruleset.cap.second_apron_by_season["2025-26"] == 199_000_000.0
    assert ruleset.trade.cash_trade_limit_percent_cap == pytest.approx(5.15)
    assert ruleset.contract.max_salary_percent_by_service == {"lt_7": 25.0, "7_to_9": 30.0, "10_plus": 35.0}
    assert ruleset.contract.annual_raise_limits["standard"] == pytest.approx(5.0)
    assert ruleset.contract.annual_raise_limits["qualifying_or_prior_team"] == pytest.approx(8.0)
    assert ruleset.cap.transaction_restrictions["A"] == "first_apron"
    assert ruleset.cap.transaction_restrictions["H"] == "second_apron"
    assert ruleset.cap.transaction_restrictions["K"] == "second_apron"
    assert "March 1" in ruleset.roster.postseason_waiver_deadline
    assert "contract.minimum_salary_scale_available" in ruleset.overrides_applied
    assert "draft.rookie_scale_table_available" in ruleset.overrides_applied
    assert report["summary"]["first_apron_2025_26"] == 187_500_000.0

