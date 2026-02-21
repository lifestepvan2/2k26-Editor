"""
Build a normalized offsets JSON and Excel workbooks from the 2K2x offset files.

Outputs:
- offsets.json
- offsets_league.json
- offsets_players.json
- offsets_jersey.json
- offsets_shoes.json
- offsets_stadiums.json
- offsets_staff.json
- offsets_teams.json
- offsets_history.json
- offsets_conversions.json (only when non-empty)
- one workbook per top type (Players.xlsx, Teams.xlsx, Jerseys.xlsx, Shoes.xlsx, Staff.xlsx, Stadiums.xlsx, Playbooks.xlsx when present)
- matching wide import workbooks for every produced top-type workbook (for example ImportPlayers.xlsx, ImportTeams.xlsx, ImportNBAHistory.xlsx)
- LeagueData.xlsx and Collisions.xlsx for diagnostics (Collisions only when non-empty)
"""
from __future__ import annotations

import json
import re
from collections import OrderedDict, defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, cast

Entry = Dict[str, Any]

import pandas as pd

ROOT = Path(__file__).parent
OUTPUT_JSON = ROOT / "offsets.json"
DIAGNOSTICS_JSON = ROOT / "offsets_diagnostics.json"
CONVERSIONS_JSON = ROOT / "offsets_conversions.json"
SPLIT_JSON_SCOPES: "OrderedDict[str, set[str]]" = OrderedDict(
    [
        ("offsets_league.json", {"League"}),
        ("offsets_players.json", {"Players"}),
        ("offsets_jersey.json", {"Jerseys"}),
        ("offsets_shoes.json", {"Shoes"}),
        ("offsets_stadiums.json", {"Stadiums"}),
        ("offsets_staff.json", {"Staff"}),
        ("offsets_teams.json", {"Teams"}),
        # History export combines NBA history and NBA records tables.
        ("offsets_history.json", {"NBA History", "NBA Records"}),
    ]
)

# Keep order stable for columns and sheets.
VERSION_FILES: "OrderedDict[str, str]" = OrderedDict(
    [
        ("2K22", "2K22_Offsets.json"),
        ("2K23", "2K23_Offsets.json"),
        ("2K24", "2K24_Offsets.json"),
        ("2K25", "2k25_offsets.json"),
        ("2K26", "2k26_offsets.json"),
    ]
)

# Collapse similar categories so we do not duplicate the same fields.
CATEGORY_NORMALIZATION = {
    "Shoes Gear": "Shoes Gear",
    "Contract": "Contracts",
    # Route pointer-style fields into player vitals instead of a separate league sheet.
    "Pointers": "Vitals",
    "TeamHistory": "Team History",
    "CareerStats": "Career Stats",
    "career_stats": "Career Stats",
}

# Treat Appearance as Vitals for these versions.
APPEARANCE_AS_VITALS = {"2K25", "2K26"}

# Some sources embed jersey subcategory in the label (including legacy typos like "Jersy"/"Jeresy").
JERSEY_PREFIX_IN_NAME_RE = re.compile(
    r"^\s*(?:jersey|jerseys|jersy|jersys|jeresy|jeresys)\s+(?P<section>vital|vitals|color|colors)\s*-\s*(?P<field>.+?)\s*$",
    flags=re.IGNORECASE,
)
TEAM_JERSEY_PREFIX_RE = re.compile(
    r"^\s*team\s+(?:jersey|jerseys|jeresy|jeresys)\s*-\s*",
    flags=re.IGNORECASE,
)

# Badges that should live under Personality regardless of source category.
PERSONALITY_BADGE_NORMALIZED = {
    "ALPHADOG",
    "ENFORCER",
    "EXPRESSIVE",
    "EXTREMELYCONFIDENT",
    "FINANCESAVVY",
    "FRIENDLY",
    "KEEPITREAL",
    "LAIDBACK",
    "MEDIARINGMASTER",
    "PATMYBACK",
    "RESERVED",
    "TEAMPLAYER",
    "UNPREDICTABLE",
    "WARMWEATHERFAN",
    "WORKETHIC",
}

# NBA history/record categories should live under dedicated super types.
NBA_HISTORY_PREFIX = "NBA History List/"
NBA_RECORD_PREFIX = "NBA Record List/"
NBA_HISTORY_CATEGORIES = [
    "Hall of Famers",
    "League Leaders",
    "Past Champions",
    "Season Awards",
]
NBA_RECORD_CATEGORIES = [
    "Career/Basic Info",
    "Career/Date Info",
    "Career/Record Stats",
    "Season/Basic Info",
    "Season/Date Info",
    "Season/Record Stats",
    "Single Game (Playoffs)/Basic Info",
    "Single Game (Playoffs)/Date Info",
    "Single Game (Playoffs)/Record Stats",
    "Single Game (Regular)/Basic Info",
    "Single Game (Regular)/Date Info",
    "Single Game (Regular)/Record Stats",
]
NBA_HISTORY_CATEGORY_SET = set(NBA_HISTORY_CATEGORIES)
NBA_RECORD_CATEGORY_SET = set(NBA_RECORD_CATEGORIES)

# Map normalized categories to super types/workbooks.
SUPER_TYPE_MAP = {
    "Appearance": "Players",
    "Attributes": "Players",
    "Badges": "Players",
    "Contract": "Players",
    "Contracts": "Players",
    "Accessories": "Players",
    "Edit": "Players",
    "Gear": "Players",
    "Hotzones": "Players",
    "Personality Badges": "Players",
    "Signatures": "Players",
    "Stats": "Players",
    "Tendencies": "Players",
    "Vitals": "Players",
    "Jersey": "Jerseys",
    "Jersey Vitals": "Jerseys",
    "Jersey Colors": "Jerseys",
    "Team Jerseys": "Teams",
    "Team Info": "Teams",
    "Team Players": "Teams",
    "Team Stats": "Teams",
    "Team Stats Edit": "Teams",
    "Team Business": "Teams",
    "Team Stadium": "Teams",
    "Team Vitals": "Teams",
    "Team Budget": "Teams",
    "Team Colors": "Teams",
    "Team Pricing": "Teams",
    "Team Uniform": "Teams",
    "Teams": "Teams",
    "Team History": "Team History",
    "History": "History",
    "Career": "Career Stats",
    "Career Stats": "Career Stats",
    "Career High Stats": "Career Stats",
    "Shoes": "Shoes",
    "Shoes Vitals": "Shoes",
    "Shoes Gear": "Shoes",
    "Staff": "Staff",
    "Staff Vitals": "Staff",
    "Staff Attributes": "Staff",
    "Staff Style": "Staff",
    "Staff Coaching": "Staff",
    "Stadium": "Stadiums",
    "Playbooks": "Playbooks",
}
SUPER_TYPE_MAP.update({cat: "NBA History" for cat in NBA_HISTORY_CATEGORIES})
SUPER_TYPE_MAP.update({cat: "NBA Records" for cat in NBA_RECORD_CATEGORIES})

SUPER_TYPE_ORDER = {
    "Players": 0,
    "Teams": 1,
    "Team History": 2,
    "History": 3,
    "Career Stats": 4,
    "Jerseys": 5,
    "Shoes": 6,
    "Staff": 7,
    "Stadiums": 8,
    "Playbooks": 9,
    "NBA History": 10,
    "NBA Records": 11,
    "League": 12,
}

# Preferred sheet order inside each workbook.
SHEET_ORDER = {
    "Players": [
        "Vitals",
        "Appearance",
        "Attributes",
        "Tendencies",
        "Badges",
    "Personality Badges",
    "Gear",
    "Accessories",
    "Hotzones",
    "Signatures",
    "Stats",
    "Contracts",
    "Edit",
],
    "Teams": [
        "Teams",
        "Team Vitals",
        "Team Info",
        "Team Players",
        "Team Stats",
        "Team Stats Edit",
        "Team Business",
        "Team Budget",
        "Team Pricing",
        "Team Colors",
        "Team Jerseys",
        "Team Stadium",
    ],
    "Team History": ["Team History"],
    "History": ["History"],
    "Career Stats": ["Career Stats", "Career High Stats", "Career"],
    "Jerseys": [
        "Jersey",
        "Jersey Vitals",
        "Jersey Colors",
    ],
    "Shoes": [
        "Shoes",
        "Shoes Vitals",
        "Shoes Gear",
    ],
    "Staff": ["Staff Vitals", "Staff Attributes", "Staff Style", "Staff Coaching", "Staff"],
    "Stadiums": ["Stadium"],
    "NBA History": list(NBA_HISTORY_CATEGORIES),
    "NBA Records": list(NBA_RECORD_CATEGORIES),
    "League": ["Pointers"],
    "Playbooks": ["Playbooks"],
}


def normalize_name(name: str, category: Optional[str] = None) -> str:
    """Normalize a field name to a stable dedupe key."""
    def replace_word_numbers(text: str) -> str:
        text = re.sub(r"[_-]+", " ", text)
        word_to_num = {
            "ZERO": "0",
            "ONE": "1",
            "TWO": "2",
            "THREE": "3",
            "FOUR": "4",
            "FIVE": "5",
            "SIX": "6",
            "SEVEN": "7",
            "EIGHT": "8",
            "NINE": "9",
            "TEN": "10",
            "ELEVEN": "11",
            "TWELVE": "12",
            "THIRTEEN": "13",
            "FOURTEEN": "14",
            "FIFTEEN": "15",
            "SIXTEEN": "16",
            "SEVENTEEN": "17",
            "EIGHTEEN": "18",
            "NINETEEN": "19",
            "TWENTY": "20",
            "THIRTY": "30",
            "FORTY": "40",
            "FIFTY": "50",
            "SIXTY": "60",
            "SEVENTY": "70",
            "EIGHTY": "80",
            "NINETY": "90",
            "HUNDRED": "100",
        }
        pattern = re.compile(r"\b(" + "|".join(word_to_num.keys()) + r")\b")
        return pattern.sub(lambda m: word_to_num[m.group(1)], text)

    upper = name.upper()
    with_numbers = replace_word_numbers(upper)
    # Normalize common fused phrases before tokenizing.
    fused_rewrites = [
        (r"MIDRANGE", "MID RANGE"),
        (r"CLOSESHOT", "CLOSE SHOT"),
        (r"SHOTCLOSE", "CLOSE SHOT"),
        (r"FREETHROWS", "FREE THROW"),
        (r"FREETHROW", "FREE THROW"),
        (r"\bORIGINAL\s+CONTRACT\s+LENGTH\b", "ORIGINAL CONTRACT YEARS"),
        (r"3[_\\s]*POINT[_\\s]*SHOT", "3 POINT"),
        (r"3POINTPOINT", "3 POINT"),
        (r"MID[_\\s]*RANGE[_\\s]*SHOT", "MID RANGE"),
        (r"MIDRANGESHOT", "MID RANGE"),
        (r"MISC(?:ELLANEOUS|ANELL?OUS)?[_\\s]*DURABILITY", "MISC DURABILITY"),
        (r"POST[_\\s]*FADE[_\\s]*AWAY", "POST FADE"),
        (r"POSTFADEAWAY", "POST FADE"),
        (r"POSTFADE", "POST FADE"),
        (r"TRANSISTION", "TRANSITION"),
        (r"PULLUP", "PULL UP"),
        (r"STEPTHROUGH", "STEP THROUGH"),
        (r"STEP THROUGH SHOT", "STEP THROUGH"),
    ]
    fused_cleaned = with_numbers
    for pat, repl in fused_rewrites:
        fused_cleaned = re.sub(pat, repl, fused_cleaned)

    # Drop trailing unit tokens so variants like WEIGHT_LBS or HEIGHTCM dedupe together.
    units_removed = re.sub(r"(?:[_\\s-]?)(LBS|CM)$", "", fused_cleaned)

    tokens = re.findall(r"[A-Z0-9]+", units_removed)

    category_upper = str(category or "").strip().upper()
    map_bare_three_to_three_point = category_upper in {"ATTRIBUTES", "TENDENCIES"}

    token_map = {
        "DEFENSIVE": "DEFENSE",
        "PASSING": "PASS",
        "PASSINGS": "PASS",
        "THROWS": "THROW",
        "SCOK": "SOCK",
        "PT": "POINT",
        "3PT": "3POINT",
        "3POINTPOINT": "3POINT",
        "SHOOT": "SHOT",
    }
    if map_bare_three_to_three_point:
        token_map["3"] = "3POINT"
    normalized_tokens: List[str] = [token_map.get(tok, tok) or tok for tok in tokens]

    # Collapse redundant POINT after 3POINT (e.g., THREE POINT -> 3POINTPOINT -> 3POINT).
    if len(normalized_tokens) >= 2 and normalized_tokens[0] == "3POINT" and normalized_tokens[1] == "POINT":
        normalized_tokens = ["3POINT"] + normalized_tokens[2:]

    # If a token set represents a shot, keep SHOT at the end for stable ordering.
    if "SHOT" in normalized_tokens and len(normalized_tokens) <= 4:
        others = sorted([tok for tok in normalized_tokens if tok != "SHOT"])
        normalized_tokens = others + ["SHOT"]

    # Drop trailing IQ token specifically for HELP DEFENSE IQ vs HELP DEFENSE variants.
    if normalized_tokens[:2] == ["HELP", "DEFENSE"] and normalized_tokens[-1] == "IQ":
        normalized_tokens = normalized_tokens[:-1]

    return "".join(normalized_tokens)


def split_jersey_prefixed_name(name: str) -> Optional[Tuple[str, str]]:
    """
    Convert labels like "Jersey Vitals - Edition Name" to
    ("Jersey Vitals", "Edition Name").
    """
    match = JERSEY_PREFIX_IN_NAME_RE.match(name)
    if not match:
        return None

    field = match.group("field").strip()
    if not field:
        return None

    section = match.group("section").lower()
    if "vital" in section:
        return ("Jersey Vitals", field)
    if "color" in section:
        return ("Jersey Colors", field)
    return None


def normalize_team_jersey_name(name: str) -> str:
    """
    Normalize team jersey labels across legacy variants:
    - Strip category prefixes like "Team Jersey -"
    - Convert #N<number> or N#<number> to #<number>
    - Canonicalize jersey slots to "Jersey #<number>"
    """
    clean = TEAM_JERSEY_PREFIX_RE.sub("", name).strip()
    clean = re.sub(r"#\s*N(?=\d)", "#", clean, flags=re.IGNORECASE)
    clean = re.sub(r"([_\s-])N#(?=\d)", r"\1#", clean, flags=re.IGNORECASE)
    clean = re.sub(r"^N#(?=\d)", "#", clean, flags=re.IGNORECASE)

    jersey_slot = re.match(r"^\s*jersey(?:[_\s-]*)#?\s*(\d+)\s*$", clean, flags=re.IGNORECASE)
    if jersey_slot:
        return f"Jersey #{int(jersey_slot.group(1))}"

    if re.match(r"^\s*practice(?:[_\s-]*)home\s*$", clean, flags=re.IGNORECASE):
        return "Practice Jersey Home"
    if re.match(r"^\s*practice(?:[_\s-]*)away\s*$", clean, flags=re.IGNORECASE):
        return "Practice Jersey Away"
    return clean


def format_version_cell(data: Dict) -> str:
    """Format per-version data for a single cell."""
    if not data:
        return ""
    addr = data.get("hex")
    if not addr and data.get("address") is not None:
        try:
            addr = hex(int(data["address"]))
        except Exception:
            addr = str(data["address"])
    meta_parts: List[str] = []
    for key in ("type", "length", "startBit", "requiresDereference", "dereferenceAddress"):
        val = data.get(key)
        if val is None:
            continue
        if key == "requiresDereference" and val is False:
            continue
        meta_parts.append(f"{key}={val}")
    if meta_parts:
        return f"{addr} ({', '.join(meta_parts)})"
    return addr or ""


HASH_NUMBER_RE = re.compile(r"^(?P<prefix>.*?#)\s*(?P<number>\d+)(?P<suffix>.*)$")


def hash_number_sort_key(text: str) -> Tuple[str, int, str]:
    """
    Natural-sort values that contain '#<number>' so #2 comes before #10,
    but only within the same base label (for example, "Jersey #2" vs "Jersey #10").
    """
    cleaned = str(text).strip()
    match = HASH_NUMBER_RE.match(cleaned)
    if not match:
        return (cleaned.upper(), -1, cleaned.upper())
    prefix = re.sub(r"\s+", " ", match.group("prefix")).strip().upper()
    suffix = re.sub(r"\s+", " ", match.group("suffix")).strip().upper()
    base = f"{prefix}{suffix}".strip()
    return (base, int(match.group("number")), cleaned.upper())


def entry_sort_key(entry: Dict[str, Any]) -> Tuple[Any, ...]:
    display = str(entry.get("display_name", ""))
    normalized = str(entry.get("normalized_name", ""))
    return (
        hash_number_sort_key(display),
        hash_number_sort_key(normalized),
        display.upper(),
        normalized.upper(),
    )


def entries_to_frame(entries: Iterable[Entry], include_variant_names: bool = True) -> pd.DataFrame:
    rows = []
    for entry in entries:
        versions: Dict[str, Dict[str, Any]] = cast(Dict[str, Dict[str, Any]], entry.get("versions", {}))
        row = {
            "Name": entry["display_name"],
            "Category": entry["canonical_category"],
            "Normalized Name": entry["normalized_name"],
        }
        if include_variant_names:
            variants: List[str] = list(cast(Iterable[str], entry.get("variant_names", [])))
            row["Variant Names"] = ", ".join(variants)
        for version, fname in VERSION_FILES.items():
            row[fname] = format_version_cell(versions.get(version, {}))
        rows.append(row)
    rows.sort(key=lambda r: (r["Category"], hash_number_sort_key(str(r["Name"])), str(r["Name"]).upper()))
    return pd.DataFrame(rows)


def entries_to_wide_frame(entries: Iterable[Entry]) -> pd.DataFrame:
    """Build a wide frame where display names are column headers and rows are empty."""
    ordered = []
    seen: Dict[str, int] = {}
    for entry in sorted(entries, key=entry_sort_key):
        name = entry["display_name"]
        seen[name] = seen.get(name, 0) + 1
        if seen[name] > 1:
            name = f"{name} ({seen[name]})"
        ordered.append(name)
    # An empty frame with only column headers; Excel will emit just the header row.
    return pd.DataFrame(columns=ordered)


def simple_name(s: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "", s.upper())


def names_match(a_norm: str, b_norm: str, a_disp: str, b_disp: str) -> bool:
    token_map = {
        "FIRST": "1",
        "PRIMARY": "1",
        "SECOND": "2",
        "SECONDARY": "2",
        "THIRD": "3",
        "FOURTH": "4",
        "FIFTH": "5",
    }

    def tokenized(name: str) -> List[str]:
        tokens = re.findall(r"[A-Z0-9]+", name.upper())
        return [token_map.get(tok, tok) or tok for tok in tokens]

    toks_a = tokenized(a_disp)
    toks_b = tokenized(b_disp)

    def is_comp_short_conflict(t1, t2) -> bool:
        def is_shorts(tok_list):
            return len(tok_list) == 1 and tok_list[0] == "SHORTS"

        def has_comp(tok_list):
            return any(tok.startswith("COMP") for tok in tok_list)

        return (is_shorts(t1) and has_comp(t2)) or (is_shorts(t2) and has_comp(t1))

    if is_comp_short_conflict(toks_a, toks_b):
        return False

    def has_color(tok_list):
        return "COLOR" in tok_list

    if "SHORTS" in toks_a and "SHORTS" in toks_b and has_color(toks_a) != has_color(toks_b):
        return False
    if "SHORTS" in toks_a and "SHORTS" in toks_b and ("LENGTH" in toks_a or "LENGTH" in toks_b):
        return False
    if "SHORTS" in toks_a and "SHORTS" in toks_b and ("PREFERRED" in toks_a or "PREFERRED" in toks_b):
        return False

    short_tok, long_tok = (toks_a, toks_b) if len(toks_a) <= len(toks_b) else (toks_b, toks_a)
    if short_tok and len(short_tok) == len(long_tok) == 1 and short_tok[0] == long_tok[0]:
        return True
    if short_tok and len(short_tok) > 1 and all(tok in long_tok for tok in short_tok):
        return True

    allow_substring = not (short_tok and len(short_tok) == 1 and len(long_tok) > 1)

    if allow_substring:
        short, long = (a_norm, b_norm) if len(a_norm) <= len(b_norm) else (b_norm, a_norm)
        if short and short in long:
            return True
        a_simple = simple_name(a_disp)
        b_simple = simple_name(b_disp)
        short, long = (a_simple, b_simple) if len(a_simple) <= len(b_simple) else (b_simple, a_simple)
        if short and short in long:
            return True

    return False


POSITION_NORMALIZED_NAMES = {"POSITION", "SECONDARYPOSITION", "THIRDPOSITION", "POSITION2"}
STAT_ID_KEY_RE = re.compile(r"^STATS?ID(?P<suffix>[A-Z0-9]+)$")
TRAILING_NUMBER_RE = re.compile(r"^(?P<prefix>[A-Z_]+?)(?P<number>\d+)$")


def stat_id_suffix(norm: str) -> Optional[str]:
    match = STAT_ID_KEY_RE.match(norm)
    if not match:
        return None
    return match.group("suffix")


def trailing_number_parts(norm: str) -> Optional[Tuple[str, int]]:
    match = TRAILING_NUMBER_RE.match(norm)
    if not match:
        return None
    return (match.group("prefix"), int(match.group("number")))


def should_skip_merge(cat: str, norm_a: str, norm_b: str) -> bool:
    # Prevent fuzzy merges like JERSEY2 with JERSEY26.
    num_a = trailing_number_parts(norm_a)
    num_b = trailing_number_parts(norm_b)
    if num_a and num_b and num_a[0] == num_b[0] and num_a[1] != num_b[1]:
        return True

    # Prevent numeric stat-id fields from fuzzy merging (e.g., STATSID1 with STATSID10).
    stat_id_a = stat_id_suffix(norm_a)
    stat_id_b = stat_id_suffix(norm_b)
    if stat_id_a and stat_id_b and stat_id_a != stat_id_b:
        return True

    if cat != "Vitals":
        # Stadium city short vs full name should remain distinct.
        if cat == "Stadium" and {norm_a, norm_b} <= {"CITYNAME", "CITYSHORTNAME"}:
            return True
        return False
    if norm_a == norm_b:
        return False
    if norm_a in POSITION_NORMALIZED_NAMES and norm_b in POSITION_NORMALIZED_NAMES:
        return True
    # Keep all shorts-related fields distinct across merge passes.
    if norm_a.startswith("SHORTS") or norm_b.startswith("SHORTS"):
        return True
    return False


def strip_nba_list_prefix(category: str) -> str:
    upper = category.upper()
    if upper.startswith(NBA_HISTORY_PREFIX.upper()):
        return category[len(NBA_HISTORY_PREFIX) :].strip()
    if upper.startswith(NBA_RECORD_PREFIX.upper()):
        return category[len(NBA_RECORD_PREFIX) :].strip()
    return category


def resolve_super_type(cat: str, raw_cat: Optional[str] = None) -> str:
    """Route a canonical category to its owning super type/workbook."""
    mapped = SUPER_TYPE_MAP.get(cat)
    if mapped:
        return mapped

    upper = cat.upper()
    raw_upper = (raw_cat or "").upper()
    if (
        upper.startswith(NBA_HISTORY_PREFIX.upper())
        or raw_upper.startswith(NBA_HISTORY_PREFIX.upper())
        or cat in NBA_HISTORY_CATEGORY_SET
    ):
        return "NBA History"
    if (
        upper.startswith(NBA_RECORD_PREFIX.upper())
        or raw_upper.startswith(NBA_RECORD_PREFIX.upper())
        or cat in NBA_RECORD_CATEGORY_SET
    ):
        return "NBA Records"
    if upper in {"TEAM HISTORY", "TEAMHISTORY"}:
        return "Team History"
    if upper in {"HISTORY"}:
        return "History"
    if upper in {"CAREER", "CAREER STATS", "CAREER_STATS", "CAREERSTATS", "CAREER HIGH STATS"}:
        return "Career Stats"
    if upper.startswith("NBA"):
        return "League"
    return "Players"


def staff_subcategory(name: str) -> str:
    """Map raw staff names to subcategories for clearer grouping."""
    upper = name.upper()
    if upper.startswith("STAFF ATTR"):
        return "Staff Attributes"
    if upper.startswith("STAFF STYLE"):
        return "Staff Style"
    if upper.startswith("STAFF COACH"):
        return "Staff Coaching"
    return "Staff Vitals"


def merge_cross_gen(entries: Dict) -> Tuple[Dict, List[Dict]]:
    """Merge rows split across old (2K22-2K24) and new (2K25-2K26) when names uniquely overlap."""
    early = {"2K22", "2K23", "2K24"}
    late = {"2K25", "2K26"}
    merge_events: List[Dict] = []

    def choose_display(names):
        for n in names:
            if not n.isupper():
                return n
        return min(names, key=len)

    def record_merge(reason: str, category: str, keep_norm: str, remove_norm: str, keep_entry: Dict, remove_entry: Dict):
        merge_events.append(
            {
                "reason": reason,
                "category": category,
                "kept_normalized_name": keep_norm,
                "removed_normalized_name": remove_norm,
                "kept_display": keep_entry.get("display_name"),
                "removed_display": remove_entry.get("display_name"),
                "kept_versions": sorted(keep_entry.get("versions", {}).keys()),
                "removed_versions": sorted(remove_entry.get("versions", {}).keys()),
            }
        )

    by_cat = defaultdict(dict)
    for (cat, norm), entry in entries.items():
        by_cat[cat][norm] = entry

    for cat, bucket in by_cat.items():
        norms = list(bucket.keys())
        used = set()
        for i in range(len(norms)):
            if norms[i] in used:
                continue
            for j in range(i + 1, len(norms)):
                if norms[j] in used:
                    continue
                if should_skip_merge(cat, norms[i], norms[j]):
                    continue
                entry_a = bucket[norms[i]]
                entry_b = bucket[norms[j]]
                versions_a = set(entry_a["versions"].keys())
                versions_b = set(entry_b["versions"].keys())
                overlap = versions_a & versions_b
                if len(overlap) < 4:
                    continue
                if not names_match(
                    entry_a["normalized_name"], entry_b["normalized_name"], entry_a["display_name"], entry_b["display_name"]
                ):
                    continue
                target_norm = norms[i] if len(norms[i]) <= len(norms[j]) else norms[j]
                keep_entry = bucket[target_norm]
                other_entry = entry_b if keep_entry is entry_a else entry_a
                keep_entry["variant_names"].update(entry_a["variant_names"])
                keep_entry["variant_names"].update(entry_b["variant_names"])
                keep_entry["versions"].update(entry_a["versions"])
                keep_entry["versions"].update(entry_b["versions"])
                keep_entry["display_name"] = choose_display(
                    list(keep_entry["variant_names"]) + [entry_a["display_name"], entry_b["display_name"]]
                )
                remove_norm = norms[j] if keep_entry is entry_a else norms[i]
                record_merge("wide_overlap", cat, target_norm, remove_norm, keep_entry, bucket[remove_norm])
                used.add(remove_norm)
                bucket.pop(remove_norm, None)
                break

        # Pass 3: general merge inside category when version sets are disjoint and name is a unique match.
        norms = list(bucket.keys())
        used.clear()
        for i in range(len(norms)):
            if norms[i] not in bucket:
                continue
            if norms[i] in used:
                continue
            entry_a = bucket[norms[i]]
            versions_a = set(entry_a["versions"].keys())
            matches = []
            for j in range(len(norms)):
                if i == j:
                    continue
                if norms[j] not in bucket:
                    continue
                if should_skip_merge(cat, norms[i], norms[j]):
                    continue
                entry_b = bucket[norms[j]]
                versions_b = set(entry_b["versions"].keys())
                if versions_a & versions_b:
                    continue
                if names_match(
                    entry_a["normalized_name"], entry_b["normalized_name"], entry_a["display_name"], entry_b["display_name"]
                ):
                    matches.append(norms[j])
            if len(matches) != 1:
                continue
            norm_b = matches[0]
            entry_b = bucket[norm_b]
            target_norm = norms[i] if len(norms[i]) <= len(norm_b) else norm_b
            keep_entry = bucket[target_norm]
            other_entry = entry_b if keep_entry is entry_a else entry_a
            keep_entry["variant_names"].update(entry_a["variant_names"])
            keep_entry["variant_names"].update(entry_b["variant_names"])
            keep_entry["versions"].update(entry_a["versions"])
            keep_entry["versions"].update(entry_b["versions"])
            keep_entry["display_name"] = choose_display(
                list(keep_entry["variant_names"]) + [entry_a["display_name"], entry_b["display_name"]]
            )
            remove_norm = norm_b if keep_entry is entry_a else norms[i]
            record_merge("disjoint_unique_match", cat, target_norm, remove_norm, keep_entry, bucket[remove_norm])
            used.add(remove_norm)
            bucket.pop(remove_norm, None)

    # Flatten back to entries dict.
    new_entries = {}
    for cat, bucket in by_cat.items():
        for norm, entry in bucket.items():
            new_entries[(cat, norm)] = entry
    return new_entries, merge_events


def build_base_pointer_frame(version_meta: Dict[str, Dict]) -> pd.DataFrame:
    pointer_names = set()
    for meta in version_meta.values():
        pointer_names.update(meta.get("base_pointers", {}).keys())
    rows = []
    for pointer in sorted(pointer_names):
        row = {"Pointer": pointer}
        for version, fname in VERSION_FILES.items():
            data = version_meta.get(version, {}).get("base_pointers", {}).get(pointer, {})
            addr = data.get("address")
            chain = data.get("chain")
            if addr is None and not chain:
                row[fname] = ""
            else:
                extra = f" chain={chain}" if chain else ""
                row[fname] = f"{addr}{extra}" if addr is not None else extra.strip()
        rows.append(row)
    return pd.DataFrame(rows)


def build_game_info_frame(version_meta: Dict[str, Dict]) -> pd.DataFrame:
    keys = set()
    for meta in version_meta.values():
        keys.update(meta.get("game_info", {}).keys())
    rows = []
    for key in sorted(keys):
        row = {"Field": key}
        for version, fname in VERSION_FILES.items():
            val = version_meta.get(version, {}).get("game_info", {}).get(key)
            row[fname] = "" if val is None else val
        rows.append(row)
    return pd.DataFrame(rows)


def collisions_to_frame(collisions: List[Dict]) -> pd.DataFrame:
    """Create a tabular view of per-version normalization collisions."""
    rows = []
    for c in collisions:
        rows.append(
            {
                "Version": str(c.get("version") or ""),
                "Category": str(c.get("canonical_category") or ""),
                "Normalized Name": str(c.get("normalized_name") or ""),
                "Assigned Normalized Name": str(c.get("assigned_normalized_name") or ""),
                "Normalized Root": str(c.get("normalized_root", c.get("normalized_name")) or ""),
                "Kept Name": str(c.get("kept_name") or ""),
                "Incoming Name": str(c.get("incoming_name") or ""),
                "Kept Category": str(c.get("kept_offset", {}).get("category") or ""),
                "Incoming Category": str(c.get("incoming_offset", {}).get("category") or ""),
                "Kept Hex": c.get("kept_hex"),
                "Incoming Hex": c.get("incoming_hex"),
                "Kept Address": c.get("kept_address"),
                "Incoming Address": c.get("incoming_address"),
                "Kept Type": c.get("kept_offset", {}).get("type"),
                "Incoming Type": c.get("incoming_offset", {}).get("type"),
                "Kept StartBit": c.get("kept_offset", {}).get("startBit"),
                "Incoming StartBit": c.get("incoming_offset", {}).get("startBit"),
                "Kept Length": c.get("kept_offset", {}).get("length"),
                "Incoming Length": c.get("incoming_offset", {}).get("length"),
                "Kept Offset JSON": json.dumps(c.get("kept_offset", {}), sort_keys=True),
                "Incoming Offset JSON": json.dumps(c.get("incoming_offset", {}), sort_keys=True),
            }
        )
    rows.sort(key=lambda r: (r["Version"], r["Category"], r["Normalized Name"], r["Incoming Name"]))
    return pd.DataFrame(rows)


def main() -> None:
    entries: Dict[Tuple[str, str], Entry] = {}
    version_meta: Dict[str, Dict[str, Any]] = {}
    duplicate_versions: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    duplicate_counter: Dict[Tuple[str, str], int] = defaultdict(int)
    run_date = date.today().isoformat()

    for version, fname in VERSION_FILES.items():
        data = json.loads(Path(ROOT / fname).read_text(encoding="utf-8"))
        game_info = dict(data.get("game_info", {}))
        game_info["version"] = run_date if version == "2K26" else version
        version_meta[version] = {
            "game_info": game_info,
            "base_pointers": data.get("base_pointers", {}),
        }

        for offset in data.get("offsets", []):
            # Skip true dropdown-only rows, but keep rows that also carry offset metadata.
            typ = offset.get("type")
            has_dropdown_payload = ("dropdown" in offset) or ("values" in offset) or (
                isinstance(typ, str) and "dropdown" in typ.lower()
            )
            has_offset_payload = any(
                offset.get(key) is not None
                for key in ("address", "hex", "length", "startBit", "requiresDereference", "dereferenceAddress")
            )
            if has_dropdown_payload and not has_offset_payload:
                continue
            sanitized_offset = {k: v for k, v in offset.items() if k not in {"dropdown", "values"}}

            raw_cat = str(sanitized_offset.get("category", "Uncategorized"))
            canon_cat = strip_nba_list_prefix(raw_cat)
            canon_cat = str(CATEGORY_NORMALIZATION.get(canon_cat, canon_cat))
            if raw_cat == "Staff":
                canon_cat = staff_subcategory(str(sanitized_offset["name"]))
            if raw_cat == "Staff Familiarity":
                # New 2K26 bucket; treat alongside other staff data so it lands in Staff workbook.
                canon_cat = "Staff Style"
            if raw_cat == "Stadium Vitals":
                # 2K26 renamed stadium category; route into existing Stadium sheet.
                canon_cat = "Stadium"
            clean_name = str(sanitized_offset["name"])
            if raw_cat == "Teams":
                # Older versions embed subcategory in the name (e.g., "Team Vitals - CITYNAME").
                match = re.match(r"Team\s+([^-]+)\s*-\s*(.+)$", clean_name, flags=re.IGNORECASE)
                if match:
                    sub = match.group(1).strip()
                    rest = match.group(2).strip()
                    sub_map = {
                        "Jersey": "Team Jerseys",
                        "Jerseys": "Team Jerseys",
                        "Jeresy": "Team Jerseys",
                        "Jeresys": "Team Jerseys",
                        "Vitals": "Team Vitals",
                        "Stats": "Team Stats",
                        "Stats Edit": "Team Stats Edit",
                        "Business": "Team Business",
                    }
                    canon_cat = sub_map.get(sub, f"Team {sub}")
                    clean_name = rest or clean_name
            jersey_name_split = split_jersey_prefixed_name(clean_name)
            raw_cat_lower = raw_cat.lower()
            if jersey_name_split and (
                canon_cat in {"Jersey", "Jersey Vitals", "Jersey Colors"}
                or raw_cat_lower.startswith("jersey")
                or raw_cat_lower.startswith("jersy")
                or raw_cat_lower.startswith("jeresy")
            ):
                canon_cat, clean_name = jersey_name_split
            if canon_cat in {"Jersey", "Jersey Vitals", "Jersey Colors"}:
                # Fix legacy typo in sock-related jersey labels (SCOK -> SOCK).
                clean_name = re.sub(r"SCOK", "SOCK", clean_name, flags=re.IGNORECASE)
            if raw_cat == "Appearance" and version in APPEARANCE_AS_VITALS:
                canon_cat = "Vitals"
            if canon_cat in {"Team Business", "Team Pricing"}:
                # Merge pricing into business so these team finance fields share one category/sheet.
                canon_cat = "Team Business"
            if canon_cat == "Team Jerseys":
                clean_name = normalize_team_jersey_name(clean_name)
            if canon_cat == "Stadium":
                # Drop category prefix from legacy stadium labels so names normalize consistently.
                clean_name = re.sub(r"^Stadium(?:\s+Vitals)?\s*-\s*", "", clean_name, flags=re.IGNORECASE)

            norm = normalize_name(clean_name, canon_cat)
            if canon_cat == "Team Jerseys":
                jersey_num_match = re.match(r"^\s*Jersey\s*#\s*(\d+)\s*$", clean_name, flags=re.IGNORECASE)
                if jersey_num_match:
                    norm = f"JERSEY{int(jersey_num_match.group(1))}"
            if canon_cat == "Team Business" and norm in {"CONCESSIONSPRICES", "CONCESSIONPRICE"}:
                # Merge plural/singular concessions price labels into the base concessions field.
                norm = "CONCESSIONS"
            if canon_cat == "Stadium" and norm in {"NAME", "ARENANAME"}:
                # Treat generic NAME and explicit ARENA NAME as the same stadium field.
                norm = "ARENANAME"
            if canon_cat == "Stadium" and norm in {"CITYABB", "CITYSHORTNAME"}:
                # Collapse legacy CITY_ABB and new City Short Name.
                norm = "CITYSHORTNAME"
            if canon_cat == "Stadium" and norm in {"FLOORFILE", "FLOORID"}:
                # Align legacy floor file with the 2K26 floor id field.
                norm = "FLOORID"
            if raw_cat == "Accessories" and "SHORTS" in norm:
                # Keep shorts accessories separate from gear to avoid collisions.
                canon_cat = "Accessories"
            if canon_cat == "Accessories" and norm == "LEFTFINGERSITEMHOMECOLRO":
                # Normalize typo'd left finger color field so 2K26 merges with prior years.
                norm = "LEFTFINGERSHOMECOLOR"
            if canon_cat == "Vitals" and norm == "FROM":
                norm = "COLLEGE"
            if canon_cat == "Vitals" and norm == "POSITION2":
                # Keep primary/secondary positions distinct; fold Position 2 into the secondary slot.
                norm = "SECONDARYPOSITION"
            if canon_cat == "Vitals" and norm == "JERSEYNUMBER":
                norm = "NUMBER"
            if canon_cat == "Badges" and norm in PERSONALITY_BADGE_NORMALIZED:
                canon_cat = "Personality Badges"
            if canon_cat == "Tendencies":
                norm = norm.replace("TENDENCY", "").replace("TENDENCIES", "")
                tend_map = {
                    "MIDRANGESHOT": "MIDSHOT",
                    "OFFSCREENSHOT3POINT": "3POINTOFFSCREENSHOT",
                    "OFFSCREENSHOTMIDRANGE": "MIDOFFSCREENSHOT",
                    "SHOT3POINTLEFTCENTER": "3POINTCENTERLEFTSHOT",
                    "SHOT3POINTRIGHTCENTER": "3POINTCENTERRIGHTSHOT",
                    "SHOTMIDLEFTCENTER": "CENTERLEFTMIDSHOT",
                    "SHOTMIDRIGHTCENTER": "CENTERMIDRIGHTSHOT",
                    "SPOTUPSHOT3POINT": "3POINTSPOTUPSHOT",
                    "SPOTUPSHOTMIDRANGE": "MIDSPOTUPSHOT",
                    "DRIVECROSSOVER": "DRIBBLECROSSOVER",
                    "DRIVESPIN": "DRIBBLESPIN",
                    "DRIVEPULLUPTHREE": "DRIVEPULLUP3POINT",
                    "TRANSITIONPULLUPTHREE": "TRANSITIONPULLUP3POINT",
                    "STEPBACKJUMPERTHREE": "STEPBACKJUMPER3POINT",
                    "CONTESTEDJUMPERTHREE": "CONTESTEDJUMPER3POINT",
                    "THREESHOT": "3POINTSHOT",
                    "CENTERTHREESHOT": "3POINTCENTERSHOT",
                    "LEFTTHREESHOT": "3POINTLEFTSHOT",
                    "RIGHTTHREESHOT": "3POINTRIGHTSHOT",
                    "DRIVINGCROSSOVER": "DRIBBLECROSSOVER",
                    "DRIVINGSPIN": "DRIBBLESPIN",
                    "DRIBBLESTEPBACK": "DRIVINGSTEPBACK",
                    "NOSETUPDRIBBLEMOVE": "NOSETUPDRIBBLE",
                    "BACKPOSTSTEPSHOT": "POSTSTEPBACKSHOT",
                    "POSTSHOT": "FROMPOSTSHOT",
                    "SHOTFROMPOST": "FROMPOSTSHOT",
                    "SHOOTFROMPOST": "FROMPOSTSHOT",
                    "BLOCK": "BLOCKSHOT",
                    "STEAL": "ONBALLSTEAL",
                    "DRIBBLEBEHINDTHEBACK": "DRIVINGBEHINDTHEBACK",
                    "DRIBBLEDOUBLECROSSOVER": "DRIVINGDOUBLECROSSOVER",
                    "DRIBBLEHALFSPIN": "DRIVINGHALFSPIN",
                }
                norm = tend_map.get(norm, norm)
            if canon_cat == "Hotzones":
                hot_map = {
                    "CENTER3POINT": "3POINTCENTER",
                    "LEFT3POINT": "3POINTLEFT",
                    "RIGHT3POINT": "3POINTRIGHT",
                    "MIDCENTER": "MIDRANGECENTER",
                }
                norm = hot_map.get(norm, norm)
            if canon_cat == "Signatures":
                sig_map = {
                    "JUMPBALLROUTINES": "JUMPBALLRITUAL",
                }
                if norm.startswith("DUNKPACKAGEAGE"):
                    norm = norm.replace("PACKAGEAGE", "PACKAGE", 1)
                elif norm.startswith("DUNKPACK") and not norm.startswith("DUNKPACKAGE"):
                    norm = norm.replace("PACK", "PACKAGE", 1)
                norm = sig_map.get(norm, norm)
            if canon_cat == "Attributes" and norm in {"3POINTSHOT", "3POINT"}:
                norm = "3POINT"
            if canon_cat == "Attributes" and norm in {"MIDRANGESHOT", "MIDRANGE"}:
                norm = "MIDRANGE"
            if canon_cat == "Attributes" and norm in {"POSTMOVES"}:
                norm = "POSTCONTROL"
            if canon_cat == "Attributes" and "MISC" in norm and "DURABILITY" in norm:
                norm = "MISCDURABILITY"
            if "+/-" in clean_name.upper() or clean_name.strip() in {"+-"}:
                # Normalize all plus/minus labels to a single box plus/minus key.
                norm = "BOX+-"
            if canon_cat == "Stats" and (norm.startswith("PLAYERSTATID") or norm.startswith("PLAYERSTATSID")):
                # Merge "Player Stat(s) ID" and "Stats ID" labels inside player stats.
                if norm.startswith("PLAYERSTATSID"):
                    norm = "STATSID" + norm[len("PLAYERSTATSID") :]
                else:
                    norm = "STATSID" + norm[len("PLAYERSTATID") :]
            if canon_cat == "Stats" and norm.startswith("STATSID"):
                # Keep stat-id suffixes numeric; avoid word expansion like 3 -> 3POINT.
                norm = re.sub(r"^STATSID([0-9]+)POINT$", r"STATSID\1", norm)
            if canon_cat == "Badges":
                badge_map = {
                    "STRONGHANDLES": "STRONGHANDLE",
                }
                norm = badge_map.get(norm, norm)
            if canon_cat == "Pointers" and norm in {"PORTRAITTEAM2"}:
                canon_cat = "Vitals"
            if not canon_cat.startswith("Staff"):
                if norm == "CONTRACTTEAM":
                    canon_cat = "Vitals"
                elif "CONTRACT" in norm and canon_cat != "Contracts":
                    canon_cat = "Contracts"
            super_type = resolve_super_type(canon_cat, raw_cat)
            key = (canon_cat, norm)

            if key not in entries:
                entries[key] = {
                    "canonical_category": canon_cat,
                    "super_type": super_type,
                    "normalized_name": norm,
                    "display_name": clean_name,
                    "variant_names": set(),
                    "versions": {},
                }

            entry = entries[key]
            entry["variant_names"].update({sanitized_offset["name"], clean_name})
            if entry["display_name"].isupper() and not clean_name.isupper():
                entry["display_name"] = clean_name

            if version in entry["versions"]:
                existing = entry["versions"][version]
                duplicate_counter[(canon_cat, norm)] += 1
                unique_norm = norm
                while (canon_cat, unique_norm) in entries:
                    unique_norm = f"{norm}__ALT{duplicate_counter[(canon_cat, norm)]}"

                duplicate_versions[version].append(
                    {
                        "version": version,
                        "canonical_category": canon_cat,
                        "normalized_name": norm,
                        "normalized_root": norm,
                        "assigned_normalized_name": unique_norm,
                        "kept_name": existing.get("name", entry["display_name"]),
                        "incoming_name": sanitized_offset["name"],
                        "kept_hex": existing.get("hex"),
                        "incoming_hex": sanitized_offset.get("hex"),
                        "kept_address": existing.get("address"),
                        "incoming_address": sanitized_offset.get("address"),
                        "kept_offset": existing,
                        "incoming_offset": sanitized_offset,
                    }
                )

                # Preserve the incoming offset as a separate entry under an alternate normalized name.
                alt_key = (canon_cat, unique_norm)
                if alt_key not in entries:
                    entries[alt_key] = {
                        "canonical_category": canon_cat,
                        "super_type": super_type,
                        "normalized_name": unique_norm,
                        "normalized_root": norm,
                        "display_name": sanitized_offset["name"],
                        "variant_names": {sanitized_offset["name"]},
                        "versions": {},
                    }
                entries[alt_key]["versions"][version] = {**sanitized_offset, "category": raw_cat}
                continue

            entry["versions"][version] = {**sanitized_offset, "category": raw_cat}

    entries, merge_events = merge_cross_gen(entries)

    mega = {
        "super_type_map": SUPER_TYPE_MAP,
        "versions": version_meta,
        "offsets": [],
    }

    for entry in entries.values():
        if entry["canonical_category"] == "Stadium":
            entry["display_name"] = re.sub(
                r"^Stadium(?:\s+Vitals)?\s*-\s*", "", entry["display_name"], flags=re.IGNORECASE
            )
        if entry["canonical_category"] == "Team Jerseys":
            entry["display_name"] = normalize_team_jersey_name(str(entry["display_name"]))
        if entry["canonical_category"] == "Stats":
            stats_id_match = re.match(r"^STATSID([0-9]+)$", str(entry["normalized_name"]))
            if stats_id_match:
                # Keep stat-id labels compact and numeric.
                entry["display_name"] = f"STATS_ID#{stats_id_match.group(1)}"

        # Strip per-version fields that should not appear in exported offsets lists.
        versions_clean: Dict[str, Dict[str, Any]] = {}
        for ver, data in entry["versions"].items():
            compact = {k: v for k, v in data.items() if k not in {"category", "name", "showHex", "dropdown", "values"}}
            versions_clean[ver] = compact

        mega["offsets"].append(
            {
                "super_type": entry["super_type"],
                "canonical_category": entry["canonical_category"],
                "normalized_name": entry["normalized_name"],
                "display_name": entry["display_name"],
                "versions": versions_clean,
            }
        )

    mega["offsets"].sort(
        key=lambda e: (
            SUPER_TYPE_ORDER.get(e["super_type"], 99),
            e["canonical_category"],
            hash_number_sort_key(str(e["display_name"])),
            str(e["normalized_name"]).upper(),
        )
    )

    # Compress identical per-version payloads in the JSON output only (Excel generation still uses full per-version keys).
    def compress_versions(versions: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Group versions that have identical payloads into a single entry keyed by comma-joined version names."""
        by_payload: Dict[str, List[str]] = defaultdict(list)
        for ver, payload in versions.items():
            key = json.dumps(payload, sort_keys=True)
            by_payload[key].append(ver)
        compressed: Dict[str, Dict[str, Any]] = {}
        for key, vers in by_payload.items():
            combined_key = ",".join(sorted(vers))
            compressed[combined_key] = json.loads(key)
        return compressed

    compressed_offsets = []
    for entry in mega["offsets"]:
        compressed_entry = {**entry, "versions": compress_versions(entry["versions"])}
        compressed_offsets.append(compressed_entry)

    OUTPUT_JSON.write_text(json.dumps({**mega, "offsets": compressed_offsets}, indent=2), encoding="utf-8")

    # Split mega output by requested top-level scopes for downstream tooling.
    def grouped_offsets_by_type_and_category(
        split_entries: List[Dict[str, Any]],
        allowed_super_types: set[str],
    ) -> Dict[str, Any]:
        def group_player_stats(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            player_stat_id: List[Dict[str, Any]] = []
            season: List[Dict[str, Any]] = []
            career: List[Dict[str, Any]] = []
            awards: List[Dict[str, Any]] = []

            for entry in entries:
                norm = str(entry.get("normalized_name", ""))
                if "STATID" in norm or "STATSID" in norm:
                    player_stat_id.append(entry)
                elif norm.endswith("SEASON") or "SEASON" in norm:
                    season.append(entry)
                elif norm.endswith("CAREER") or "CAREER" in norm:
                    career.append(entry)
                else:
                    # Default bucket for non-season/career/id player stats.
                    awards.append(entry)

            player_stat_id.sort(key=entry_sort_key)
            season.sort(key=entry_sort_key)
            career.sort(key=entry_sort_key)
            awards.sort(key=entry_sort_key)

            return [
                {"Player Stat ID": player_stat_id},
                {"Season": season},
                {"Career": career},
                {"Awards": awards},
            ]

        payload: Dict[str, Any] = {}
        ordered_types = sorted(allowed_super_types, key=lambda s: (SUPER_TYPE_ORDER.get(s, 99), s))
        for super_type in ordered_types:
            super_entries = [entry for entry in split_entries if entry["super_type"] == super_type]
            by_category: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
            for entry in super_entries:
                category = cast(str, entry["canonical_category"])
                # Category/type are represented by grouping containers, so keep entry payload minimal.
                compact_entry = {
                    k: v for k, v in entry.items() if k not in {"super_type", "canonical_category"}
                }
                by_category[category].append(compact_entry)

            grouped_categories: List[Dict[str, Any]] = []
            for category in sorted(by_category):
                category_entries = sorted(by_category[category], key=entry_sort_key)
                if super_type == "Players" and category == "Stats":
                    grouped_categories.append({category: group_player_stats(category_entries)})
                else:
                    grouped_categories.append({category: category_entries})
            payload[f"{super_type} offsets"] = grouped_categories
        return payload

    for split_name, allowed_super_types in SPLIT_JSON_SCOPES.items():
        filtered_offsets = [entry for entry in compressed_offsets if entry["super_type"] in allowed_super_types]
        if split_name == "offsets_league.json":
            # League owns global metadata used by downstream consumers.
            split_payload: Dict[str, Any] = {
                "super_type_map": dict(SUPER_TYPE_MAP),
                "versions": mega["versions"],
            }
        else:
            # Type-specific payloads are grouped by super type then canonical category.
            split_payload = grouped_offsets_by_type_and_category(filtered_offsets, allowed_super_types)
        (ROOT / split_name).write_text(json.dumps(split_payload, indent=2), encoding="utf-8")

    # Cross-version conversion hints (metadata only; no calculations applied).
    def entry_stub(cat: str, norm: str) -> Dict[str, Optional[str]]:
        ref = entries.get((cat, norm))
        return {
            "canonical_category": cat,
            "normalized_name": norm,
            "display_name": ref.get("display_name") if ref else norm,
        }

    conversions = [
        {
            "source": entry_stub("Attributes", "AGILITY"),
            "targets": [
                entry_stub("Attributes", "ACCELERATION"),
                entry_stub("Attributes", "LATERALQUICKNESS"),
            ],
        }
    ]

    if conversions:
        CONVERSIONS_JSON.write_text(json.dumps(conversions, indent=2), encoding="utf-8")
    elif CONVERSIONS_JSON.exists():
        CONVERSIONS_JSON.unlink()

    missing_2k26 = []
    for entry in mega["offsets"]:
        versions_present = sorted(entry["versions"].keys())
        if "2K26" not in versions_present and versions_present:
            missing_2k26.append(
                {
                    "canonical_category": entry["canonical_category"],
                    "normalized_name": entry["normalized_name"],
                    "display_name": entry["display_name"],
                    "variant_names": entry.get("variant_names", []),
                    "present_versions": versions_present,
                }
            )

    duplicate_report = []
    for version, conflicts in duplicate_versions.items():
        duplicate_report.extend(conflicts)
    duplicate_report.sort(
        key=lambda d: (d["version"], d["canonical_category"], d["normalized_name"], d["incoming_name"])
    )

    diagnostics = {"collisions": duplicate_report}
    if duplicate_report:
        DIAGNOSTICS_JSON.write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    elif DIAGNOSTICS_JSON.exists():
        DIAGNOSTICS_JSON.unlink()

    # Write collision workbook to make reviewing normalization conflicts easier.
    collisions_path = ROOT / "Collisions.xlsx"
    collisions_df = collisions_to_frame(duplicate_report)
    if not collisions_df.empty:
        try:
            with pd.ExcelWriter(collisions_path, engine="openpyxl") as writer:
                collisions_df.to_excel(writer, sheet_name="Collisions", index=False)
        except PermissionError:
            print("Warning: Collisions.xlsx is locked; skipping collisions workbook generation.")
    elif collisions_path.exists():
        try:
            collisions_path.unlink()
        except PermissionError:
            print("Warning: Collisions.xlsx is locked; cannot remove stale collisions workbook.")

    # Build workbooks from the mega data.
    grouped_by_super: Dict[str, Dict[str, List[Entry]]] = defaultdict(lambda: defaultdict(list))  # type: ignore[var-annotated]
    playbook_entries: List[Entry] = []

    for entry in mega["offsets"]:
        grouped_by_super[entry["super_type"]][entry["canonical_category"]].append(entry)
        if entry["canonical_category"] == "Playbooks" and "PLAYBOOK" in entry["normalized_name"]:
            playbook_entries.append(entry)

    def sorted_categories(super_type: str, sheets: Dict[str, List[Entry]]) -> Iterable[Tuple[str, List[Entry]]]:
        order = SHEET_ORDER.get(super_type, [])
        used = set()
        for cat in order:
            cat_entries = sheets.get(cat, [])
            if not cat_entries:
                continue
            used.add(cat)
            yield cat, cat_entries
        for cat, cat_entries in sorted(sheets.items()):
            if cat in used or not cat_entries:
                continue
            yield cat, cat_entries

    INVALID_SHEET_CHARS = re.compile(r"[\\/*?:\\[\\]]")

    def sanitize_sheet_name(name: str, used: set[str]) -> str:
        """Excel-safe, unique sheet names."""
        clean = re.sub(r"[\\/]", " - ", name)
        clean = INVALID_SHEET_CHARS.sub(" ", clean)
        clean = re.sub(r"\s+", " ", clean).strip() or "Sheet"

        def truncate(text: str) -> str:
            return text[:31]

        base = truncate(clean)
        candidate = base
        counter = 1
        while candidate in used:
            suffix = f" {counter}"
            max_len = 31 - len(suffix)
            candidate = truncate(base[:max_len]) + suffix
            counter += 1
        used.add(candidate)
        return candidate

    def write_workbook(super_type: str, path: Path, sheets: Dict[str, List[Entry]]) -> None:
        if not sheets:
            return
        used_names: set[str] = set()
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            for cat, cat_entries in sorted_categories(super_type, sheets):
                sheet_name = sanitize_sheet_name(cat, used_names)
                entries_to_frame(cat_entries, include_variant_names=False).to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=False,
                )

    def write_workbook_wide(super_type: str, path: Path, sheets: Dict[str, List[Entry]]) -> None:
        if not sheets:
            return
        used_names: set[str] = set()
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            for cat, cat_entries in sorted_categories(super_type, sheets):
                sheet_name = sanitize_sheet_name(cat, used_names)
                entries_to_wide_frame(cat_entries).to_excel(writer, sheet_name=sheet_name, index=False)

    super_type_overrides: Dict[str, Dict[str, List[Entry]]] = {}
    if playbook_entries:
        super_type_overrides["Playbooks"] = {"Playbooks": playbook_entries}

    def super_type_sort_key(super_type: str) -> Tuple[int, str]:
        return (SUPER_TYPE_ORDER.get(super_type, 99), super_type)

    ordered_super_types = sorted(
        set(grouped_by_super.keys()) | set(super_type_overrides.keys()),
        key=super_type_sort_key,
    )

    import_enabled = set(ordered_super_types)

    for super_type in ordered_super_types:
        sheets = super_type_overrides.get(super_type, grouped_by_super.get(super_type, {}))
        if not sheets:
            continue
        safe_name = super_type.replace(" ", "")
        write_workbook(super_type, ROOT / f"{safe_name}.xlsx", sheets)
        if super_type in import_enabled:
            write_workbook_wide(super_type, ROOT / f"Import{safe_name}.xlsx", sheets)

    # League data workbook.
    league_sheets: Dict[str, List[Entry]] = grouped_by_super.get("League", {})
    with pd.ExcelWriter(ROOT / "LeagueData.xlsx", engine="openpyxl") as writer:
        league_used: set[str] = set()
        for cat, cat_entries in sorted_categories("League", league_sheets):
            sheet_name = sanitize_sheet_name(cat, league_used)
            entries_to_frame(cat_entries).to_excel(writer, sheet_name=sheet_name, index=False)
        base_df = build_base_pointer_frame(version_meta)
        if not base_df.empty:
            sheet_name = sanitize_sheet_name("BasePointers", league_used)
            base_df.to_excel(writer, sheet_name=sheet_name, index=False)
        game_info_df = build_game_info_frame(version_meta)
        if not game_info_df.empty:
            sheet_name = sanitize_sheet_name("GameInfo", league_used)
            game_info_df.to_excel(writer, sheet_name=sheet_name, index=False)


if __name__ == "__main__":
    main()
