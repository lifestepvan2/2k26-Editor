from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..gm_rl.cba.extractors import extract_raw_rules, load_manifest, load_manual_overrides
from ..gm_rl.cba.normalizer import normalize_rules, ruleset_to_all_years_payload


def _default_source() -> Path:
    return Path(__file__).resolve().parents[1] / "CBA" / "2023-NBA-Collective-Bargaining-Agreement.docx"


def _default_outdir() -> Path:
    return Path(__file__).resolve().parents[1] / "gm_rl" / "cba"


def main(args: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Extract CBA rules for NBA 2K AI GM")
    parser.add_argument("--season", type=str, default="2025-26")
    parser.add_argument("--source", type=str, default=str(_default_source()))
    parser.add_argument("--outdir", type=str, default=str(_default_outdir()))
    parser.add_argument("--manifest", type=str, default=None)
    parser.add_argument("--overrides", type=str, default=None)
    parsed = parser.parse_args(args)

    manifest = load_manifest(Path(parsed.manifest)) if parsed.manifest else load_manifest()
    overrides = load_manual_overrides(Path(parsed.overrides)) if parsed.overrides else load_manual_overrides()

    raw, citations = extract_raw_rules(parsed.source, manifest=manifest)
    ruleset, report = normalize_rules(
        raw,
        citations,
        season=parsed.season,
        manifest=manifest,
        overrides=overrides,
    )

    outdir = Path(parsed.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    rules_single_path = outdir / "rules_2025_26.json"
    rules_all_path = outdir / "rules_all_years.json"
    report_path = outdir / "extraction_report_2025_26.json"

    rules_single_path.write_text(json.dumps(ruleset.to_dict(), indent=2), encoding="utf-8")
    rules_all_path.write_text(json.dumps(ruleset_to_all_years_payload(ruleset), indent=2), encoding="utf-8")
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Wrote {rules_single_path}")
    print(f"Wrote {rules_all_path}")
    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()

