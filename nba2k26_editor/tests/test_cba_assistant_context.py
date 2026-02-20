from __future__ import annotations

from nba2k_editor.ai.cba_context import build_cba_guidance


def test_cba_guidance_contains_core_constraints():
    guidance = build_cba_guidance(season="2025-26")
    # Guidance may be empty if rules are unavailable in a consumer environment,
    # but in-repo extraction writes baseline artifacts that should satisfy this.
    assert "first apron" in guidance.lower()
    assert "cash" in guidance.lower()
    assert "roster" in guidance.lower()

