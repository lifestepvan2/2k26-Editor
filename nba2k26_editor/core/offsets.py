"""
Offset loading and schema normalization.

Handles:
* offset file discovery and parsing
* canonical field lookup helpers
* resolved constants for player/team tables
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, cast

from .config import MODULE_NAME as CONFIG_MODULE_NAME
from .conversions import to_int
from .offset_cache import CachedOffsetPayload, OffsetCache
from .offset_loader import OffsetRepository
from .offset_resolver import OffsetResolveError, OffsetResolver
from .perf import timed


class OffsetSchemaError(RuntimeError):
    """Raised when offsets are missing required definitions."""


BASE_POINTER_SIZE_KEY_MAP: dict[str, str | None] = {
    "Player": "playerSize",
    "Team": "teamSize",
    "Staff": "staffSize",
    "Stadium": "stadiumSize",
    "TeamHistory": "historySize",
    "NBAHistory": "historySize",
    "HallOfFame": "hall_of_fameSize",
    "History": "historySize",
    "Jersey": "jerseySize",
    "career_stats": "career_statsSize",
    "Cursor": None,
}
REQUIRED_LIVE_BASE_POINTER_KEYS: tuple[str, ...] = ("Player", "Team", "Staff", "Stadium")

STRICT_OFFSET_FIELD_KEYS: dict[str, tuple[str, str]] = {
    "player_first_name": ("Vitals", "FIRSTNAME"),
    "player_last_name": ("Vitals", "LASTNAME"),
    "player_current_team": ("Vitals", "CURRENTTEAM"),
    "team_name": ("Team Vitals", "TEAMNAME"),
    "team_city_name": ("Team Vitals", "CITYNAME"),
    "team_city_abbrev": ("Team Vitals", "CITYABBREV"),
    "staff_first_name": ("Staff Vitals", "FIRSTNAME"),
    "staff_last_name": ("Staff Vitals", "LASTNAME"),
    "stadium_name": ("Stadium", "ARENANAME"),
}

MODULE_NAME = CONFIG_MODULE_NAME
OFFSET_FILENAME_PATTERNS: tuple[str, ...] = ()
SPLIT_OFFSETS_LEAGUE_FILE = "offsets_league.json"
SPLIT_OFFSETS_DOMAIN_FILES: tuple[str, ...] = (
    "offsets_players.json",
    "offsets_teams.json",
    "offsets_staff.json",
    "offsets_stadiums.json",
    "offsets_history.json",
    "offsets_shoes.json",
)
SPLIT_OFFSETS_OPTIONAL_FILES: tuple[str, ...] = ("dropdowns.json",)
OFFSETS_BUNDLE_FILE = "split offsets files (offsets_league.json + offsets_*.json)"
PLAYER_STATS_TABLE_CATEGORY_MAP: dict[str, str] = {
    "player stat id": "Stats - IDs",
    "season": "Stats - Season",
    "career": "Stats - Career",
    "awards": "Stats - Awards",
}
PLAYER_STATS_IDS_CATEGORY = "Stats - IDs"
PLAYER_STATS_SEASON_CATEGORY = "Stats - Season"
_offset_file_path: Path | None = None
_offset_config: dict | None = None
_offset_config_primary: dict | None = None
_offset_file_path_primary: Path | None = None
_offset_config_offsets2: dict | None = None
_offset_file_path_offsets2: Path | None = None
_offset_index: dict[tuple[str, str], dict] = {}
_offset_normalized_index: dict[tuple[str, str], dict] = {}
_current_offset_target: str | None = None
_base_pointer_overrides: dict[str, int] | None = None
CATEGORY_SUPER_TYPES: dict[str, str] = {}
CATEGORY_CANONICAL: dict[str, str] = {}
PLAYER_STATS_RELATIONS: dict[str, Any] = {}

_OFFSET_CACHE = OffsetCache()
_OFFSET_REPOSITORY = OffsetRepository(_OFFSET_CACHE)

PLAYER_TABLE_RVA = 0
PLAYER_STRIDE = 0
PLAYER_PTR_CHAINS: list[dict[str, object]] = []
DRAFT_PTR_CHAINS: list[dict[str, object]] = []
OFF_LAST_NAME = 0
OFF_FIRST_NAME = 0
OFF_TEAM_PTR = 0
OFF_TEAM_NAME = 0
OFF_TEAM_ID = 0
MAX_PLAYERS = 5500
MAX_DRAFT_PLAYERS = 150
DRAFT_CLASS_TEAM_ID = -2
MAX_TEAMS_SCAN = 400
NAME_MAX_CHARS = 20
FIRST_NAME_ENCODING = "utf16"
LAST_NAME_ENCODING = "utf16"
TEAM_NAME_ENCODING = "utf16"
TEAM_STRIDE = 0
TEAM_NAME_OFFSET = 0
TEAM_NAME_LENGTH = 0
TEAM_PLAYER_SLOT_COUNT = 30
TEAM_PTR_CHAINS: list[dict[str, object]] = []
TEAM_TABLE_RVA = 0
TEAM_FIELD_DEFS: dict[str, tuple[int, int, str]] = {}
TEAM_RECORD_SIZE = TEAM_STRIDE

TEAM_FIELD_SPECS: tuple[tuple[str, str, str], ...] = (
    ("Team Name", "Team Vitals", "TEAMNAME"),
    ("City Name", "Team Vitals", "CITYNAME"),
    ("City Abbrev", "Team Vitals", "CITYABBREV"),
)
PLAYER_PANEL_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("Position", "Vitals", "Position"),
    ("Number", "Vitals", "Jersey Number"),
    ("Height", "Vitals", "Height"),
    ("Weight", "Vitals", "Weight"),
    ("Face ID", "Vitals", "Face ID"),
    ("Unique ID", "Vitals", "UNIQUESIGNATUREID"),
)
PLAYER_PANEL_OVR_FIELD: tuple[str, str] = ("Attributes", "CACHCED_OVR")

UNIFIED_FILES: tuple[str, ...] = ()
EXTRA_CATEGORY_FIELDS: dict[str, list[dict]] = {}

# Staff/Stadium metadata (populated when offsets define them)
STAFF_STRIDE = 0
STAFF_PTR_CHAINS: list[dict[str, object]] = []
STAFF_RECORD_SIZE = STAFF_STRIDE
STAFF_NAME_OFFSET = 0
STAFF_NAME_LENGTH = 0
STAFF_NAME_ENCODING = "utf16"
MAX_STAFF_SCAN = 400

STADIUM_STRIDE = 0
STADIUM_PTR_CHAINS: list[dict[str, object]] = []
STADIUM_RECORD_SIZE = STADIUM_STRIDE
STADIUM_NAME_OFFSET = 0
STADIUM_NAME_LENGTH = 0
STADIUM_NAME_ENCODING = "utf16"
MAX_STADIUM_SCAN = 200

ATTR_IMPORT_ORDER = [
    "Driving Layup",
    "Standing Dunk",
    "Driving Dunk",
    "Close Shot",
    "Mid Range",
    "Three Point",
    "Free Throw",
    "Post Hook",
    "Post Fade",
    "Post Control",
    "Draw Foul",
    "Shot IQ",
    "Ball Control",
    "Speed With Ball",
    "Hands",
    "Passing Accuracy",
    "Passing IQ",
    "Passing Vision",
    "Offensive Consistency",
    "Interior Defense",
    "Perimeter Defense",
    "Steal",
    "Block",
    "Offensive Rebound",
    "Defensive Rebound",
    "Help Defense IQ",
    "Passing Perception",
    "Defensive Consistency",
    "Speed",
    "Agility",
    "Strength",
    "Vertical",
    "Stamina",
    "Intangibles",
    "Hustle",
    "Misc Durability",
    "Potential",
]
DUR_IMPORT_ORDER = [
    "Back Durability",
    "Head Durability",
    "Left Ankle Durability",
    "Left Elbow Durability",
    "Left Foot Durability",
    "Left Hip Durability",
    "Left Knee Durability",
    "Left Shoulder Durability",
    "Neck Durability",
    "Right Ankle Durability",
    "Right Elbow Durability",
    "Right Foot Durability",
    "Right Hip Durability",
    "Right Knee Durability",
    "Right Shoulder Durability",
    "Misc Durability",
]
POTENTIAL_IMPORT_ORDER = [
    "Minimum Potential",
    "Potential",
    "Maximum Potential",
]

NAME_SYNONYMS: dict[str, list[str]] = {
    "cam": ["Cameron"],
    "cameron": ["Cam"],
    "nic": ["Nicolas"],
    "nicolas": ["Nic"],
    "rob": ["Robert"],
    "robert": ["Rob"],
    "ron": ["Ronald"],
    "ronald": ["Ron"],
    "nate": ["Nathan"],
    "nathan": ["Nate"],
}
NAME_SUFFIXES: set[str] = {"jr", "sr", "ii", "iii", "iv", "v"}

TEND_IMPORT_ORDER = [
    "Shot Three Right Center",
    "Shot Three Left Center",
    "Off Screen Shot Three",
    "Shot Three Right",
    "Spot Up Shot Three",
    "Alley Oop Pass",
    "Attack Strong On Drive",
    "Shot Under Basket",
    "Block Tendency",
    "Shot Mid Right Center",
    "Shot Close Middle",
    "Shot Close Right",
    "Shot Close Left",
    "Contested Jumper Three",
    "Contested Jumper Mid",
    "Contest Shot",
    "Crash",
    "Dish To Open Man",
    "Dribble Double Crossover",
    "Dribble Half Spin",
    "Drive",
    "Drive Pull Up Three",
    "Drive Pull Up Mid",
    "Drive Right",
    "Dribble Behind The Back",
    "Driving Dribble Hesitation",
    "Driving Dunk Tendency",
    "Driving In And Out",
    "Driving Layup Tendency",
    "Dribble Stepback",
    "Euro Step Layup",
    "Flashy Dunk",
    "Flashy Pass",
    "Floater",
    "Foul",
    "Post Shoot",
    "Hard Foul",
    "Post Hop Shot",
    "Hop Step Layup",
    "Iso Vs Average Defender",
    "Iso Vs Elite Defender",
    "Iso Vs Good Defender",
    "Iso Vs Poor Defender",
    "Shot Mid Left Center",
    "Off Screen Shot Mid",
    "Shot Mid Right",
    "Spot Up Shot Mid",
    "No Driving Dribble Move",
    "No Setup Dribble Move",
    "Off Screen Drive",
    "Steal Tendency",
    "Pass Interception",
    "Play Discipline",
    "Post Aggressive Backdown",
    "Post Back Down",
    "Post Drive",
    "Post Dropstep",
    "Post Fade Left",
    "Post Fade Right",
    "Post Hook Left",
    "Post Hook Right",
    "Post Hop Step",
    "Post Shimmy Shot",
    "Post Spin",
    "Post Stepback Shot",
    "Post Face Up",
    "Post Up And Under",
    "Putback Dunk",
    "Roll Vs Pop",
    "Setup With Hesitation",
    "Setup With Sizeup",
    "Shot Tendency",
    "Spin Jumper",
    "Spin Layup",
    "Spot Up Drive",
    "Standing Dunk Tendency",
    "Stepback Jumper Three",
    "Step Back Jumper Mid",
    "Step Through",
    "Take Charge",
    "Triple Threat Shoot",
    "Touches",
    "Transition Pull Up Three",
    "Transition Spot Up",
    "Triple Threat Idle",
    "Triple Threat Jab Step",
    "Triple Threat Pump Fake",
    "Use Glass",
]


FIELD_NAME_ALIASES: dict[str, str] = {
    "SHOT": "SHOOT",
    "SHOTTENDENCY": "SHOOT",
    "SHOTSHOT": "SHOOT",
    "SHOTATTRIBUTE": "SHOOT",
    "SHOTMIDRANGE": "SHOTMID",
    "SPOTUPSHOTMIDRANGE": "SPOTUPSHOTMID",
    "OFFSCREENSHOTMIDRANGE": "OFFSCREENSHOTMID",
    "SHOTTHREE": "SHOT3PT",
    "SPOTUPSHOTTHREE": "SPOTUPSHOT3PT",
    "OFFSCREENSHOTTHREE": "OFFSCREENSHOT3PT",
    "SHOTTHREELEFT": "SHOT3PTLEFT",
    "SHOTTHREELEFTCENTER": "SHOT3PTLEFTCENTER",
    "SHOTTHREECENTER": "SHOT3PTCENTER",
    "SHOTTHREERIGHTCENTER": "SHOT3PTRIGHTCENTER",
    "SHOTTHREERIGHT": "SHOT3PTRIGHT",
    "CONTESTEDJUMPERMIDRANGE": "CONTESTEDJUMPERMID",
    "CONTESTEDJUMPERTHREE": "CONTESTEDJUMPER3PT",
    "STEPBACKJUMPERMIDRANGE": "STEPBACKJUMPERMID",
    "STEPBACKJUMPERTHREE": "STEPBACKJUMPER3PT",
    "SPINJUMPER": "SPINJUMPERTENDENCY",
    "TRANSITIONPULLUPTHREE": "TRANSITIONPULLUP3PT",
    "DRIVEPULLUPMIDRANGE": "DRIVEPULLUPMID",
    "DRIVEPULLUPTHREE": "DRIVEPULLUP3PT",
    "EUROSTEPLAYUP": "EUROSTEP",
    "HOPSTEPLAYUP": "HOPSTEP",
    "STANDINGDUNK": "STANDINGDUNKTENDENCY",
    "DRIVINGDUNK": "DRIVINGDUNKTENDENCY",
    "FLASHYDUNK": "FLASHYDUNKTENDENCY",
    "DRIVINGBEHINDTHEBACK": "DRIVINGBEHINDBACK",
    "DRIVINGINANDOUT": "INANDOUT",
    "NODRIVINGDRIBBLEMOVE": "NODRIBBLE",
    "TRANSITIONSPOTUP": "SPOTUPCUT",
    "ISOVSELITEDEFENDER": "ISOVSE",
    "ISOVSGOODDEFENDER": "ISOVSG",
    "ISOVSAVERAGEDEFENDER": "ISOVSA",
    "ISOVSPOORDEFENDER": "ISOVSP",
    "SHOOTFROMPOST": "POSTSHOT",
    "POSTSHIMMYSHOT": "POSTSHIMMY",
    "ONBALLSTEAL": "STEAL",
    "BLOCKSHOT": "BLOCK",
    "CONTESTSHOT": "CONTEST",
    "3PTSHOT": "THREEPOINT",
    "MIDRANGESHOT": "MIDRANGE",
    "FREETHROWS": "FREETHROW",
    "POSTMOVES": "POSTCONTROL",
    "PASSACCURACY": "PASSINGACCURACY",
    "PASSPERCEPTION": "PASSINGPERCEPTION",
    "MISCANELLOUSDURABILITY": "MISCDURABILITY",
    "SHOT3PTCENTER": "SHOT3PTRIGHTCENTER",
    "SHOT3PTLEFT": "SHOT3PTLEFTCENTER",
    "ALLEYOOPPASS": "ALLEYOOP",
    "BLOCKTENDENCY": "BLOCK",
    "DRIVINGCROSSOVER": "DRIBBLECROSSOVER",
    "DRIBBLEDOUBLECROSSOVER": "DRIBBLECROSSOVER",
    "DRIBBLEBEHINDTHEBACK": "DRIVINGBEHINDBACK",
    "DRIBBLESTEPBACK": "DRIVINGSTEPBACK",
    "POSTSHOOT": "POSTSHOT",
    "POSTHOPSHOTTENDENCY": "POSTHOPSHOT",
    "SPOTUPSHOTMID": "MIDSHOT",
    "SHOTMID": "MIDSHOT",
    "NOSETUPDRIBBLEMOVE": "NOSETUPDRIBBLE",
    "STEALTENDENCY": "STEAL",
    "POSTFACEUP": "POSTUP",
    "STEPTHROUGHSHOT": "STEPTHROUGH",
}


def _derive_offset_candidates(target_executable: str | None) -> tuple[str, ...]:
    """Return the split-offset file manifest."""
    del target_executable  # split files are not executable-specific
    return (SPLIT_OFFSETS_LEAGUE_FILE, *SPLIT_OFFSETS_DOMAIN_FILES)


def _split_version_tokens(raw_key: object) -> tuple[str, ...]:
    text = str(raw_key or "").strip()
    if not text:
        return ()
    tokens = [chunk.strip().upper() for chunk in text.split(",") if chunk and chunk.strip()]
    return tuple(dict.fromkeys(tokens))


def _version_key_matches(raw_key: object, target_label: str | None) -> bool:
    target = str(target_label or "").strip().upper()
    if not target:
        return False
    tokens = _split_version_tokens(raw_key)
    if tokens:
        return target in tokens
    return str(raw_key or "").strip().upper() == target


def _select_version_entry(per_version: dict[str, object], target_label: str) -> dict[str, object] | None:
    for raw_key, payload in per_version.items():
        if not isinstance(payload, dict):
            continue
        if _version_key_matches(raw_key, target_label):
            return payload
    return None


def _infer_length_bits(field_type: object, length_raw: object) -> int:
    length_val = to_int(length_raw)
    if length_val > 0:
        return length_val
    type_name = str(field_type or "").strip().lower()
    if type_name in {"integer", "int", "uint", "number", "slider"}:
        return 32
    if type_name == "float":
        return 32
    if "pointer" in type_name or type_name == "ptr":
        return 64
    if type_name in {"binary", "bool", "boolean", "bit", "bitfield"}:
        return 1
    return 0


def _normalize_offset_type(field_type: object) -> str:
    raw = str(field_type or "").strip().lower()
    if not raw:
        return ""
    if raw in {"integer", "int", "uint", "number", "slider", "byte", "short"}:
        return "integer"
    if raw in {"float", "single", "double"}:
        return "float"
    if "pointer" in raw or raw in {"ptr", "address"}:
        return "pointer"
    if raw in {"binary", "bool", "boolean", "bit", "bitfield", "combo"}:
        return "binary"
    if raw in {"wstring", "utf16", "utf-16", "wchar", "wide"}:
        return "wstring"
    if raw in {"string", "text", "ascii", "char", "cstring"}:
        return "string"
    return raw


def _read_json_cached(path: Path) -> dict[str, Any] | None:
    cached = _OFFSET_CACHE.get_json(path)
    if cached is not None:
        return cached
    try:
        with path.open("r", encoding="utf-8") as handle:
            parsed = json.load(handle)
    except Exception:
        return None
    if not isinstance(parsed, dict):
        return None
    _OFFSET_CACHE.set_json(path, parsed)
    return parsed


def _build_dropdown_values_index(raw_dropdowns: object) -> dict[tuple[str, str, str], list[str]]:
    index: dict[tuple[str, str, str], list[str]] = {}
    if not isinstance(raw_dropdowns, dict):
        return index
    dropdown_entries = raw_dropdowns.get("dropdowns")
    if not isinstance(dropdown_entries, list):
        return index
    for entry in dropdown_entries:
        if not isinstance(entry, dict):
            continue
        canonical_category = str(entry.get("canonical_category") or "").strip()
        normalized_name = str(entry.get("normalized_name") or "").strip()
        versions = entry.get("versions")
        if not canonical_category or not normalized_name or not isinstance(versions, dict):
            continue
        category_key = canonical_category.lower()
        normalized_key = normalized_name.upper()
        for version_key, value in versions.items():
            if not isinstance(value, dict):
                continue
            values = value.get("values")
            if not isinstance(values, list):
                values = value.get("dropdown")
            if not isinstance(values, list):
                continue
            cleaned_values = [str(item) for item in values]
            if not cleaned_values:
                continue
            for token in _split_version_tokens(version_key):
                index[(category_key, normalized_key, token)] = cleaned_values
    return index


def _resolve_split_category(root_category: str, table_segments: tuple[str, ...]) -> str:
    """Return runtime category name for a split offsets leaf entry."""
    root = str(root_category or "").strip() or "Misc"
    if root.lower() != "stats":
        return root
    if not table_segments:
        return "Stats - Misc"
    table_key = str(table_segments[0] or "").strip().lower()
    mapped = PLAYER_STATS_TABLE_CATEGORY_MAP.get(table_key)
    if mapped:
        return mapped
    table_label = str(table_segments[0]).strip()
    return f"Stats - {table_label}" if table_label else "Stats - Misc"


def _collect_split_leaf_nodes(
    node: object,
    path_segments: tuple[str, ...],
    out: list[tuple[dict[str, object], tuple[str, ...]]],
) -> None:
    if isinstance(node, list):
        for item in node:
            _collect_split_leaf_nodes(item, path_segments, out)
        return
    if not isinstance(node, dict):
        return

    versions_raw = node.get("versions")
    normalized_raw = (
        node.get("normalized_name")
        or node.get("canonical_name")
        or node.get("name")
        or node.get("display_name")
    )
    if isinstance(versions_raw, dict) and normalized_raw:
        out.append((cast(dict[str, object], node), path_segments))
        return

    for key, child in node.items():
        if not isinstance(child, (dict, list)):
            continue
        child_path = path_segments + (str(key),)
        _collect_split_leaf_nodes(child, child_path, out)


def _append_split_domain_entries(
    *,
    category_name: str,
    node: object,
    source_domain: str,
    source_file: str,
    super_type_map: dict[str, str],
    dropdown_values: dict[tuple[str, str, str], list[str]],
    out: list[dict[str, object]],
    entry_counter: list[int],
) -> None:
    leaf_nodes: list[tuple[dict[str, object], tuple[str, ...]]] = []
    _collect_split_leaf_nodes(node, (category_name,), leaf_nodes)
    for leaf_node, path_segments in leaf_nodes:
        versions_raw = leaf_node.get("versions")
        normalized_raw = (
            leaf_node.get("normalized_name")
            or leaf_node.get("canonical_name")
            or leaf_node.get("name")
            or leaf_node.get("display_name")
        )
        if not isinstance(versions_raw, dict) or not normalized_raw:
            continue

        source_root_category = str(path_segments[0] if path_segments else category_name).strip() or category_name
        source_table_segments = tuple(str(seg).strip() for seg in path_segments[1:] if str(seg).strip())
        source_table_group = source_table_segments[0] if source_table_segments else ""
        source_table_path = "/".join((source_root_category, *source_table_segments)) if source_table_segments else source_root_category
        emitted_category = _resolve_split_category(source_root_category, source_table_segments)

        canonical_category = str(leaf_node.get("canonical_category") or emitted_category).strip() or emitted_category
        normalized_name = str(normalized_raw).strip()
        if not normalized_name:
            continue
        display_name = str(leaf_node.get("display_name") or leaf_node.get("name") or normalized_name).strip() or normalized_name
        super_type = (
            leaf_node.get("super_type")
            or leaf_node.get("superType")
            or super_type_map.get(canonical_category.lower())
            or super_type_map.get(emitted_category.lower())
            or super_type_map.get(source_root_category.lower())
            or ""
        )

        version_map: dict[str, dict[str, object]] = {}
        for version_key, version_payload in versions_raw.items():
            if not isinstance(version_payload, dict):
                continue
            normalized_payload: dict[str, object] = dict(version_payload)
            if not isinstance(normalized_payload.get("values"), list):
                dropdown_categories = (
                    canonical_category,
                    str(leaf_node.get("canonical_category") or ""),
                    emitted_category,
                    source_root_category,
                )
                for token in _split_version_tokens(version_key):
                    added_values = False
                    for dropdown_category in dropdown_categories:
                        if not dropdown_category:
                            continue
                        values = dropdown_values.get((dropdown_category.lower(), normalized_name.upper(), token))
                        if values:
                            normalized_payload["values"] = list(values)
                            added_values = True
                            break
                    if added_values:
                        break
            version_map[str(version_key)] = normalized_payload
        if not version_map:
            continue

        entry_counter[0] += 1
        entry: dict[str, object] = {
            "category": emitted_category,
            "name": display_name,
            "display_name": display_name,
            "canonical_category": canonical_category,
            "normalized_name": normalized_name,
            "versions": version_map,
            "source_root_category": source_root_category,
            "source_table_group": source_table_group,
            "source_table_path": source_table_path,
            "source_offsets_domain": source_domain,
            "source_offsets_file": source_file,
            "parse_report_entry_id": int(entry_counter[0]),
        }
        # Stats tables are explicitly split into table categories with no flat alias.
        if emitted_category.startswith("Stats - "):
            entry["canonical_category"] = emitted_category
        if str(super_type or "").strip():
            entry["super_type"] = str(super_type)
        if isinstance(leaf_node.get("variant_names"), list):
            entry["variant_names"] = list(leaf_node.get("variant_names") or [])
        if leaf_node.get("canonical_name"):
            entry["canonical_name"] = str(leaf_node.get("canonical_name"))
        if leaf_node.get("type"):
            entry["type"] = leaf_node.get("type")
        out.append(entry)


def _build_split_offsets_payload(offsets_dir: Path) -> tuple[Path, dict[str, Any]] | None:
    league_path = offsets_dir / SPLIT_OFFSETS_LEAGUE_FILE
    if not league_path.is_file():
        return None
    missing_domains = [name for name in SPLIT_OFFSETS_DOMAIN_FILES if not (offsets_dir / name).is_file()]
    if missing_domains:
        return None

    league_raw = _read_json_cached(league_path)
    if not isinstance(league_raw, dict):
        return None
    versions = league_raw.get("versions")
    if not isinstance(versions, dict) or not versions:
        return None
    super_type_map_raw = league_raw.get("super_type_map")
    super_type_map: dict[str, str] = {}
    if isinstance(super_type_map_raw, dict):
        super_type_map = {str(key).lower(): str(value) for key, value in super_type_map_raw.items()}

    dropdown_values: dict[tuple[str, str, str], list[str]] = {}
    dropdown_path = offsets_dir / SPLIT_OFFSETS_OPTIONAL_FILES[0]
    if dropdown_path.is_file():
        dropdown_values = _build_dropdown_values_index(_read_json_cached(dropdown_path))

    merged_offsets: list[dict[str, object]] = []
    entry_counter = [0]
    for file_name in SPLIT_OFFSETS_DOMAIN_FILES:
        file_path = offsets_dir / file_name
        raw_domain = _read_json_cached(file_path)
        if not isinstance(raw_domain, dict):
            return None
        for domain_key, sections in raw_domain.items():
            if not isinstance(sections, list):
                continue
            for section in sections:
                if not isinstance(section, dict):
                    continue
                for category_name, payload in section.items():
                    _append_split_domain_entries(
                        category_name=str(category_name).strip() or "Misc",
                        node=payload,
                        source_domain=str(domain_key).strip() or str(file_name),
                        source_file=file_name,
                        super_type_map=super_type_map,
                        dropdown_values=dropdown_values,
                        out=merged_offsets,
                        entry_counter=entry_counter,
                    )
    if not merged_offsets:
        return None

    merged_payload: dict[str, Any] = {
        "offsets": merged_offsets,
        "versions": dict(versions),
        "_split_manifest": {
            "required_files": [SPLIT_OFFSETS_LEAGUE_FILE, *SPLIT_OFFSETS_DOMAIN_FILES],
            "optional_files": list(SPLIT_OFFSETS_OPTIONAL_FILES),
            "discovered_leaf_fields": len(merged_offsets),
        },
    }
    if isinstance(super_type_map_raw, dict):
        merged_payload["super_type_map"] = dict(super_type_map_raw)
    category_normalization = league_raw.get("category_normalization")
    if isinstance(category_normalization, dict):
        merged_payload["category_normalization"] = dict(category_normalization)
    if isinstance(league_raw.get("game_info"), dict):
        merged_payload["game_info"] = dict(league_raw.get("game_info") or {})
    if isinstance(league_raw.get("base_pointers"), dict):
        merged_payload["base_pointers"] = dict(league_raw.get("base_pointers") or {})
    return league_path, merged_payload


def _select_merged_offset_entry(raw: object, target_executable: str | None) -> dict | None:
    """
    Pick the best offsets entry from a merged offsets payload.
    Supports:
      1) a single offsets object with an `offsets` list
      2) a mapping of version keys -> offsets objects
    """
    if isinstance(raw, dict) and isinstance(raw.get("offsets"), list):
        return raw
    version_hint = None
    if target_executable:
        match = re.search(r"2k(\d{2})", target_executable.lower())
        if match:
            version_hint = match.group(1)
    if isinstance(raw, dict):
        best: dict | None = None
        best_score = -1
        for key, value in raw.items():
            if not isinstance(value, dict) or not isinstance(value.get("offsets"), list):
                continue
            score = 0
            key_lower = str(key).lower()
            game_info = value.get("game_info") if isinstance(value.get("game_info"), dict) else {}
            exec_name = str(game_info.get("executable", "")).lower() if isinstance(game_info, dict) else ""
            # Only accept entries that explicitly match the loaded game's executable (or 2kXX hint).
            if target_executable and exec_name and exec_name != target_executable.lower():
                continue
            if version_hint and not (version_hint in key_lower or version_hint in exec_name):
                continue
            if version_hint and version_hint in key_lower:
                score += 3
            if target_executable and exec_name == target_executable.lower():
                score += 4
            elif version_hint and version_hint in exec_name:
                score += 2
            version_field = str(game_info.get("version", "")).lower() if isinstance(game_info, dict) else ""
            if version_hint and version_hint in version_field:
                score += 1
            if score > best_score:
                best_score = score
                best = value
        if best:
            return best
        for value in raw.values():
            if isinstance(value, dict) and isinstance(value.get("offsets"), list):
                return value
    if isinstance(raw, list):
        for entry in raw:
            if isinstance(entry, dict) and isinstance(entry.get("offsets"), list):
                return entry
    return None


def _build_player_stats_relations(offsets: list[dict[str, object]]) -> dict[str, object]:
    id_entries: list[dict[str, object]] = []
    season_entries: list[dict[str, object]] = []
    for entry in offsets:
        if not isinstance(entry, dict):
            continue
        category = str(entry.get("canonical_category") or entry.get("category") or "").strip()
        if category == PLAYER_STATS_IDS_CATEGORY:
            id_entries.append(entry)
        elif category == PLAYER_STATS_SEASON_CATEGORY:
            season_entries.append(entry)

    def _entry_sort_key(item: dict[str, object]) -> tuple[int, int, str]:
        return (
            to_int(item.get("address")),
            to_int(item.get("startBit") or item.get("start_bit")),
            str(item.get("normalized_name") or item.get("name") or ""),
        )

    def _id_sort_key(item: dict[str, object]) -> tuple[int, int, int, str]:
        normalized = str(item.get("normalized_name") or "").strip().upper()
        if normalized.startswith("STATSID"):
            suffix = normalized.replace("STATSID", "", 1)
            return (0, int(suffix or 0) if suffix.isdigit() else 0, 0, normalized)
        if normalized == "CURRENTYEARSTATID":
            return (1, 0, 0, normalized)
        addr, bit, name = _entry_sort_key(item)
        return (2, addr, bit, name)

    ordered_ids = [
        str(item.get("normalized_name") or item.get("name") or "").strip()
        for item in sorted(id_entries, key=_id_sort_key)
        if str(item.get("normalized_name") or item.get("name") or "").strip()
    ]
    ordered_season = [
        str(item.get("normalized_name") or item.get("name") or "").strip()
        for item in sorted(season_entries, key=_entry_sort_key)
        if str(item.get("normalized_name") or item.get("name") or "").strip()
    ]
    return {
        "source_category": PLAYER_STATS_IDS_CATEGORY,
        "target_category": PLAYER_STATS_SEASON_CATEGORY,
        "relation_type": "season_only",
        "id_fields": ordered_ids,
        "target_fields": ordered_season,
    }


def _extract_player_stats_relations(config_data: dict | None) -> dict[str, Any]:
    if not isinstance(config_data, dict):
        return {}
    relations = config_data.get("relations")
    if not isinstance(relations, dict):
        return {}
    relation = relations.get("player_stats")
    if not isinstance(relation, dict):
        return {}
    return dict(relation)


def _sync_player_stats_relations(config_data: dict | None) -> None:
    global PLAYER_STATS_RELATIONS
    PLAYER_STATS_RELATIONS = _extract_player_stats_relations(config_data)


def _convert_merged_offsets_schema(raw: object, target_exe: str | None) -> dict | None:
    """Handle merged offsets schema where each entry carries per-version data."""
    if not isinstance(raw, dict):
        return None
    offsets = raw.get("offsets")
    versions_map = raw.get("versions")
    if not isinstance(offsets, list) or not isinstance(versions_map, dict):
        return None

    version_hint = None
    if target_exe:
        match = re.search(r"2k(\d{2})", target_exe.lower())
        if match:
            version_hint = f"2K{match.group(1)}"
    if version_hint is None:
        return None

    version_key: str | None = None
    for key in versions_map.keys():
        if _version_key_matches(key, version_hint):
            version_key = str(key)
            break
    if version_key is None:
        return None
    version_info = versions_map.get(version_key)
    if not isinstance(version_info, dict):
        return None

    unified_offsets: list[dict[str, object]] = []
    skipped_entries: list[dict[str, object]] = []
    skips_by_reason: dict[str, int] = {}
    discovered_leaf_fields = 0

    def _record_skip(entry_obj: dict[str, object], reason: str, **extra: object) -> None:
        skips_by_reason[reason] = skips_by_reason.get(reason, 0) + 1
        record: dict[str, object] = {
            "reason": reason,
            "category": str(entry_obj.get("category") or ""),
            "canonical_category": str(entry_obj.get("canonical_category") or ""),
            "normalized_name": str(entry_obj.get("normalized_name") or ""),
            "source_root_category": str(entry_obj.get("source_root_category") or ""),
            "source_table_path": str(entry_obj.get("source_table_path") or ""),
            "source_offsets_file": str(entry_obj.get("source_offsets_file") or ""),
            "parse_report_entry_id": to_int(entry_obj.get("parse_report_entry_id")),
        }
        for key_name, value in extra.items():
            record[str(key_name)] = value
        skipped_entries.append(record)

    for entry in offsets:
        if not isinstance(entry, dict):
            continue
        discovered_leaf_fields += 1

        per_version = entry.get("versions")
        if not isinstance(per_version, dict):
            _record_skip(cast(dict[str, object], entry), "missing_versions")
            continue
        v_entry = _select_version_entry(per_version, version_hint)
        if not isinstance(v_entry, dict):
            _record_skip(
                cast(dict[str, object], entry),
                "missing_target_version",
                available_versions=[str(key) for key in per_version.keys()],
            )
            continue

        address_raw = v_entry.get("address")
        if address_raw in (None, ""):
            address_raw = v_entry.get("offset")
        if address_raw in (None, ""):
            address_raw = v_entry.get("hex")
        if address_raw in (None, ""):
            _record_skip(cast(dict[str, object], entry), "missing_address")
            continue
        address = to_int(address_raw)
        if address < 0:
            _record_skip(cast(dict[str, object], entry), "invalid_address", address=address_raw)
            continue

        field_type_raw = v_entry.get("type") or entry.get("type")
        field_type_normalized = _normalize_offset_type(field_type_raw)
        explicit_length = to_int(v_entry.get("length"))
        length_bits = explicit_length
        length_inferred = False
        if length_bits <= 0:
            if field_type_normalized in {"wstring", "string"}:
                _record_skip(cast(dict[str, object], entry), "missing_required_string_length")
                continue
            length_bits = _infer_length_bits(field_type_raw, v_entry.get("length"))
            if length_bits <= 0:
                _record_skip(cast(dict[str, object], entry), "missing_length")
                continue
            length_inferred = True

        start_raw = v_entry.get("startBit")
        if start_raw in (None, ""):
            start_raw = v_entry.get("start_bit")
        start_bit_inferred = False
        if start_raw in (None, ""):
            start_bit = 0
            start_bit_inferred = True
        else:
            start_bit = to_int(start_raw)
            if start_bit < 0:
                start_bit = 0
                start_bit_inferred = True

        category = str(
            v_entry.get("category")
            or entry.get("category")
            or entry.get("canonical_category")
            or entry.get("super_type")
            or entry.get("superType")
            or "Misc"
        ).strip() or "Misc"
        canonical_category = str(v_entry.get("canonical_category") or entry.get("canonical_category") or category).strip() or category
        normalized_name = str(
            v_entry.get("normalized_name")
            or entry.get("normalized_name")
            or entry.get("canonical_name")
            or entry.get("name")
            or ""
        ).strip()
        if not normalized_name:
            _record_skip(cast(dict[str, object], entry), "missing_normalized_name")
            continue
        super_type = str(
            v_entry.get("super_type")
            or entry.get("super_type")
            or entry.get("superType")
            or ""
        ).strip()
        display_name = str(
            v_entry.get("name")
            or entry.get("display_name")
            or entry.get("name")
            or normalized_name
        ).strip() or normalized_name

        new_entry: dict[str, object] = {
            "category": category,
            "name": display_name,
            "display_name": display_name,
            "canonical_category": canonical_category,
            "normalized_name": normalized_name,
            "super_type": super_type,
            # Preserve both keys since downstream consumers check for `address` or `offset`.
            "address": address,
            "offset": address,
            "hex": f"0x{address:X}",
            "length": int(length_bits),
            "startBit": int(start_bit),
            "type_normalized": field_type_normalized,
            "length_inferred": bool(length_inferred),
            "start_bit_inferred": bool(start_bit_inferred),
            "selected_version": version_hint,
            "selected_version_key": version_key,
            "version_metadata": dict(v_entry),
        }
        field_type_text = str(field_type_raw or "").strip()
        if field_type_text:
            new_entry["type"] = field_type_text
        if v_entry.get("requiresDereference") is True or v_entry.get("requires_deref") is True:
            new_entry["requiresDereference"] = True
        deref = v_entry.get("dereferenceAddress")
        if deref in (None, ""):
            deref = v_entry.get("deref_offset")
        if deref in (None, ""):
            deref = v_entry.get("dereference_address")
        if deref not in (None, ""):
            new_entry["dereferenceAddress"] = to_int(deref)
        values = v_entry.get("values")
        if isinstance(values, list):
            new_entry["values"] = list(values)

        for meta_key in (
            "canonical_name",
            "variant_names",
            "source_root_category",
            "source_table_group",
            "source_table_path",
            "source_offsets_domain",
            "source_offsets_file",
            "parse_report_entry_id",
        ):
            if meta_key in entry:
                meta_value = entry.get(meta_key)
                if meta_value not in (None, ""):
                    if meta_key == "variant_names" and isinstance(meta_value, list):
                        new_entry[meta_key] = list(meta_value)
                    else:
                        new_entry[meta_key] = meta_value
        unified_offsets.append(new_entry)

    if not unified_offsets:
        return None

    skipped_fields = len(skipped_entries)
    emitted_fields = len(unified_offsets)
    accounted_fields = emitted_fields + skipped_fields
    untracked_loss = max(0, discovered_leaf_fields - accounted_fields)
    parse_report: dict[str, object] = {
        "target_version": version_hint,
        "selected_version_key": version_key,
        "discovered_leaf_fields": discovered_leaf_fields,
        "emitted_fields": emitted_fields,
        "skipped_fields": skipped_fields,
        "accounted_fields": accounted_fields,
        "untracked_loss": untracked_loss,
        "skips_by_reason": dict(sorted(skips_by_reason.items())),
        "skipped": skipped_entries,
    }

    player_stats_relations = _build_player_stats_relations(unified_offsets)

    converted: dict[str, object] = {
        "offsets": unified_offsets,
        "relations": {"player_stats": player_stats_relations},
        "_parse_report": parse_report,
    }
    # Preserve helpers that inform category grouping/canonicalization.
    if isinstance(raw.get("category_normalization"), dict):
        converted["category_normalization"] = raw["category_normalization"]
    if isinstance(raw.get("super_type_map"), dict):
        converted["super_type_map"] = raw["super_type_map"]
    converted["versions"] = {version_key: version_info}
    base_ptrs = version_info.get("base_pointers") if isinstance(version_info.get("base_pointers"), dict) else None
    if base_ptrs:
        converted["base_pointers"] = base_ptrs
    game_info = version_info.get("game_info") if isinstance(version_info.get("game_info"), dict) else None
    if game_info:
        converted["game_info"] = game_info
    return converted


def _load_offset_config_file(target_executable: str | None = None) -> tuple[Path | None, dict | None]:
    """Locate and parse split offsets files for the given executable."""
    with timed("offsets.load_offset_config_file"):
        target_key = (target_executable or "").lower()
        if target_key:
            cached = _OFFSET_CACHE.get_target(target_key)
            if cached is not None:
                return cached.path, dict(cached.data)
        base_dir = Path(__file__).resolve().parent.parent
        search_dirs = [
            base_dir / "Offsets",
            base_dir / "offsets",
        ]
        resolver = OffsetResolver(
            convert_schema=_convert_merged_offsets_schema,
            select_entry=_select_merged_offset_entry,
        )
        for folder in search_dirs:
            split_payload = _build_split_offsets_payload(folder)
            if split_payload is None:
                continue
            path, raw_payload = split_payload
            resolved = resolver.resolve(raw_payload, target_executable)
            if not isinstance(resolved, dict):
                continue
            payload = dict(resolved)
            if target_key:
                _OFFSET_CACHE.set_target(CachedOffsetPayload(path=path, target_key=target_key, data=payload))
            return path, payload
        return None, None


def _build_offset_index(offsets: list[dict]) -> None:
    """Create strict exact-match lookup maps for offsets entries."""
    _offset_index.clear()
    _offset_normalized_index.clear()
    for entry in offsets:
        if not isinstance(entry, dict):
            continue
        category_raw = str(entry.get("category", "")).strip()
        name_raw = str(entry.get("name", "")).strip()
        if not name_raw:
            continue
        _offset_index[(category_raw, name_raw)] = entry
        canonical = str(entry.get("canonical_category", "")).strip()
        normalized = str(entry.get("normalized_name", "")).strip()
        if canonical and normalized:
            _offset_normalized_index[(canonical, normalized)] = entry


def _find_offset_entry(name: str, category: str | None = None) -> dict | None:
    """Return the offset entry matching the provided exact name/category."""
    exact_name = name.strip()
    if category:
        return _offset_index.get((category.strip(), exact_name))
    for (cat, entry_name), entry in _offset_index.items():
        if entry_name == exact_name and (category is None or cat == category.strip()):
            return entry
    return None


def _find_offset_entry_by_normalized(canonical_category: str, normalized_name: str) -> dict | None:
    """Return an offsets entry by exact canonical_category + normalized_name."""
    return _offset_normalized_index.get((canonical_category, normalized_name))


def _load_dropdowns_map() -> dict[str, dict[str, list[str]]]:
    """Load dropdown metadata once per process from Offsets/dropdowns.json when present."""
    with timed("offsets.load_dropdowns"):
        base_dir = Path(__file__).resolve().parent.parent
        search_dirs = [base_dir / "Offsets", base_dir / "offsets"]
        return _OFFSET_REPOSITORY.load_dropdowns(search_dirs=search_dirs)


def _derive_version_label(executable: str | None) -> str | None:
    """Return a version label like '2K26' based on the executable name."""
    if not executable:
        return None
    m = re.search(r"2k(\d{2})", executable.lower())
    if not m:
        return None
    return f"2K{m.group(1)}"


def _resolve_version_context(
    data: dict[str, Any] | None,
    target_executable: str | None,
) -> tuple[str | None, dict[str, Any], dict[str, Any]]:
    """Return (version_label, base_pointers, game_info) for the active target."""
    version_label = _derive_version_label(target_executable)
    if not isinstance(data, dict):
        return version_label, {}, {}

    versions_raw = data.get("versions")
    versions_map = versions_raw if isinstance(versions_raw, dict) else {}
    version_info: dict[str, Any] = {}
    if version_label and versions_map:
        candidate = versions_map.get(version_label)
        if not isinstance(candidate, dict):
            candidate = versions_map.get(version_label.upper())
        if not isinstance(candidate, dict):
            candidate = versions_map.get(version_label.lower())
        if isinstance(candidate, dict):
            version_info = candidate

    base_pointers_source = data.get("base_pointers")
    if isinstance(base_pointers_source, dict):
        base_pointers = base_pointers_source
    else:
        version_base = version_info.get("base_pointers")
        base_pointers = version_base if isinstance(version_base, dict) else {}

    game_info_source = data.get("game_info")
    game_info = game_info_source if isinstance(game_info_source, dict) else {}
    version_game = version_info.get("game_info")
    if isinstance(version_game, dict):
        game_info = version_game

    return version_label, base_pointers, game_info


def _load_categories() -> dict[str, list[dict]]:
    """
    Load editor categories from the active offsets payload.
    Returns a dictionary mapping category names to lists of field
    definitions. If parsing fails or no offsets are available, an empty
    dictionary is returned.
    """
    dropdowns = _load_dropdowns_map()
    CATEGORY_SUPER_TYPES.clear()
    CATEGORY_CANONICAL.clear()
    category_normalization: dict[str, str] = {}
    try:
        if isinstance(_offset_config, dict):
            raw_norm = _offset_config.get("category_normalization")
            if isinstance(raw_norm, dict):
                category_normalization = {str(k).lower(): str(v) for k, v in raw_norm.items()}
    except Exception:
        category_normalization = {}

    super_type_map: dict[str, str] = {}
    try:
        if isinstance(_offset_config, dict):
            raw_map = _offset_config.get("super_type_map")
            if isinstance(raw_map, dict):
                super_type_map = {str(k).lower(): str(v) for k, v in raw_map.items()}
    except Exception:
        super_type_map = {}

    super_type_mismatches: set[str] = set()

    def _emit_super_type_warnings() -> None:
        if not super_type_mismatches:
            return
        warning_text = " ; ".join(sorted(super_type_mismatches))
        print(f"Offset warnings: super_type_map overrides: {warning_text}")

    def _register_category_metadata(cat_label: str, entry: dict | None = None) -> None:
        """Capture super type and canonical label for a category."""
        if not cat_label:
            return
        cat_key = str(cat_label)
        if cat_key not in CATEGORY_SUPER_TYPES:
            entry_super = None
            if isinstance(entry, dict):
                entry_super = entry.get("super_type") or entry.get("superType")
            map_super = super_type_map.get(cat_key.lower())
            # Allow explicit mapping to override mis-labeled entries (e.g., team tabs tagged as Players).
            if map_super:
                if entry_super and str(entry_super).lower() != str(map_super).lower():
                    super_type_mismatches.add(f"{cat_key}: {entry_super} -> {map_super}")
                entry_super = map_super
            if entry_super is None:
                cat_lower = cat_key.lower()
                if cat_lower.startswith("team "):
                    entry_super = "Teams"
            if entry_super:
                CATEGORY_SUPER_TYPES[cat_key] = str(entry_super)
        if cat_key not in CATEGORY_CANONICAL:
            canonical = None
            if isinstance(entry, dict):
                canonical = entry.get("canonical_category")
            if canonical is None:
                canonical = category_normalization.get(cat_key.lower())
            CATEGORY_CANONICAL[cat_key] = str(canonical) if canonical else cat_key

    def _finalize_field_metadata(
        field: dict[str, object],
        category_label: str,
        *,
        offset_val: int | None = None,
        start_bit_val: int | None = None,
        length_val: int | None = None,
        source_entry: dict | None = None,
    ) -> None:
        """Ensure each field dictionary carries core offset metadata."""
        if not isinstance(field, dict):
            return
        if category_label:
            field["category"] = category_label
        provided_hex = None
        if source_entry is not None and source_entry.get("hex"):
            provided_hex = str(source_entry.get("hex"))
        if offset_val is None:
            offset_val = to_int(field.get("address") or field.get("offset") or field.get("hex"))
        if offset_val is not None and offset_val >= 0:
            offset_int = int(offset_val)
            field["address"] = offset_int
            field.setdefault("offset", hex(offset_int))
            if provided_hex is None:
                provided_hex = f"0x{offset_int:X}"
        if provided_hex is not None:
            field["hex"] = provided_hex
        if "startBit" not in field or field.get("startBit") in (None, ""):
            start_val = start_bit_val
            if start_val is None:
                start_val = to_int(field.get("start_bit"))
            field["startBit"] = int(start_val or 0)
        if "start_bit" in field and "startBit" in field:
            field.pop("start_bit", None)
        if "length" not in field or to_int(field.get("length")) <= 0:
            length = length_val
            if length is None:
                length = to_int(field.get("length") or field.get("size"))
            if length is not None and length > 0:
                field["length"] = int(length)
        if source_entry is not None and source_entry.get("type") and not field.get("type"):
            field["type"] = source_entry.get("type")
        if source_entry is not None:
            for key_name in (
                "canonical_category",
                "normalized_name",
                "super_type",
                "type_normalized",
                "source_root_category",
                "source_table_group",
                "source_table_path",
                "source_offsets_domain",
                "source_offsets_file",
                "length_inferred",
                "start_bit_inferred",
                "parse_report_entry_id",
                "selected_version",
                "selected_version_key",
            ):
                if source_entry.get(key_name) and not field.get(key_name):
                    field[key_name] = source_entry.get(key_name)

    def _entry_to_field(entry: dict, display_name: str, target_category: str | None = None) -> dict | None:
        offset_val = to_int(entry.get("address"))
        length_val = to_int(entry.get("length"))
        if offset_val <= 0 or length_val <= 0:
            return None
        start_bit = to_int(entry.get("startBit"))
        field: dict[str, object] = {
            "name": display_name,
            "offset": hex(offset_val),
            "startBit": int(start_bit),
            "length": int(length_val),
        }
        if entry.get("requiresDereference"):
            field["requiresDereference"] = True
            field["dereferenceAddress"] = to_int(entry.get("dereferenceAddress"))
        raw_type = entry.get("type")
        normalized_type = entry.get("type_normalized")
        if raw_type not in (None, ""):
            field["type_raw"] = raw_type
        if normalized_type not in (None, ""):
            field["type_normalized"] = normalized_type
            field["type"] = normalized_type
        elif raw_type not in (None, ""):
            field["type"] = raw_type
        if "values" in entry and isinstance(entry["values"], list):
            field["values"] = entry["values"]
        category_label = target_category or str(entry.get("category", "")).strip()
        _finalize_field_metadata(
            field,
            category_label,
            offset_val=offset_val,
            start_bit_val=start_bit,
            length_val=length_val,
            source_entry=entry,
        )
        return field

    def _humanize_label(raw: object) -> str:
        text = str(raw or "").strip()
        if not text:
            return ""
        tokens = [tok for tok in re.split(r"[^A-Za-z0-9]+", text) if tok]
        if not tokens:
            return text
        words: list[str] = []
        for tok in tokens:
            if tok.isupper() and len(tok) <= 3:
                words.append(tok)
            else:
                words.append(tok.capitalize())
        return " ".join(words)

    def _template_entry_to_field(cat_label: str, entry: dict, name_prefix: str | None = None) -> dict | None:
        if not isinstance(entry, dict):
            return None
        display_name = str(entry.get("name", "")).strip()
        if not display_name:
            return None
        if name_prefix:
            prefix = name_prefix.strip()
            if prefix:
                display_name = f"{prefix} - {display_name}" if display_name else prefix
        entry_type = str(entry.get("type", "")).strip().lower()
        if entry_type in {"blank", "folder", "section", "class"}:
            return None
        offset_val = to_int(entry.get("offset") or entry.get("address"))
        if offset_val < 0:
            return None
        info = entry.get("info") if isinstance(entry.get("info"), dict) else {}
        start_raw = entry.get("startBit") or entry.get("start_bit")
        if isinstance(info, dict):
            start_info = info.get("startbit") or info.get("startBit") or info.get("bit_start")
            if start_info is not None:
                start_raw = start_info
        explicit_start = start_raw is not None
        start_bit = to_int(start_raw)
        if start_bit < 0:
            start_bit = 0
        length_bits = to_int(entry.get("length"))
        if length_bits <= 0:
            size_val = to_int(entry.get("size"))
            if entry_type in {"combo", "bitfield", "bool", "boolean"}:
                length_bits = size_val
            else:
                length_bits = size_val * 8
        if length_bits <= 0 and isinstance(info, dict):
            length_bits = to_int(info.get("length") or info.get("bits"))
        if length_bits <= 0:
            return None
        if entry_type in {"combo", "bitfield", "bool", "boolean"} and not explicit_start:
            key = (cat_label, offset_val)
            start_bit = bit_cursor.get(key, 0)
        field: dict[str, object] = {
            "name": display_name,
            "offset": hex(offset_val),
            "startBit": int(start_bit),
            "length": int(length_bits),
        }
        if entry.get("type"):
            field["type"] = entry["type"]
        if isinstance(info, dict):
            options = info.get("options")
            if isinstance(options, list):
                values: list[str] = []
                for opt in options:
                    if isinstance(opt, dict):
                        label = str(opt.get("name") or opt.get("label") or opt.get("value") or "").strip()
                        if label:
                            values.append(label)
                    elif isinstance(opt, str):
                        label = opt.strip()
                        if label:
                            values.append(label)
                if values:
                    field.setdefault("values", values)
            if info.get("isptr"):
                deref = to_int(info.get("offset") or info.get("deviation"))
                if deref > 0:
                    field["requiresDereference"] = True
                    field["dereferenceAddress"] = deref
        _finalize_field_metadata(
            field,
            cat_label,
            offset_val=offset_val,
            start_bit_val=int(start_bit),
            length_val=int(length_bits),
            source_entry=entry,
        )
        return field

    def _compose_field_prefix(base_label: str | None, subgroup: str | None) -> str | None:
        base_clean = _humanize_label(base_label) if base_label else ""
        sub_clean = _humanize_label(subgroup) if subgroup else ""
        if base_clean and sub_clean:
            if base_clean.lower() == sub_clean.lower():
                return base_clean
            return f"{base_clean} {sub_clean}"
        return base_clean or sub_clean or None

    def _convert_template_payload(target_category: str, base_prefix: str | None, payload: object) -> list[dict]:
        fields: list[dict] = []
        if isinstance(payload, list):
            prefix = _compose_field_prefix(base_prefix, None)
            for item in payload:
                field = _template_entry_to_field(target_category, item, prefix)
                if field:
                    fields.append(field)
            return fields
        if isinstance(payload, dict):
            for key, entries in payload.items():
                if not isinstance(entries, list):
                    continue
                prefix = _compose_field_prefix(base_prefix, key)
                for item in entries:
                    field = _template_entry_to_field(target_category, item, prefix)
                    if field:
                        fields.append(field)
        return fields

    def _merge_extra_template_files(cat_map: dict[str, list[dict]]) -> None:
        """Template merging is disabled."""
        return

    base_categories: dict[str, list[dict]] = {}
    bit_cursor: dict[tuple[str, int], int] = {}
    seen_fields_global: dict[str, set[str]] = {}
    if isinstance(_offset_config, dict):
        categories: dict[str, list[dict]] = {}
        combined_sections: list[dict] = []

        def _extend(section: object) -> None:
            if isinstance(section, list):
                combined_sections.extend(item for item in section if isinstance(item, dict))

        _extend(_offset_config.get("offsets"))
        for key, value in _offset_config.items():
            if key in {"offsets", "game_info", "base_pointers"}:
                continue
            _extend(value)
        seen_fields: set[tuple[str, str]] = set()
        for entry in combined_sections:
            cat_name = str(entry.get("category", "Misc")).strip() or "Misc"
            field_name = str(entry.get("name", "")).strip()
            if not field_name:
                continue
            _register_category_metadata(cat_name, entry)
            key = (cat_name.lower(), field_name.lower())
            if key in seen_fields:
                continue
            seen_fields.add(key)
            offset_val = to_int(entry.get("address"))
            if offset_val < 0:
                continue
            start_bit = to_int(entry.get("startBit"))
            length_val = to_int(entry.get("length"))
            size_val = to_int(entry.get("size"))
            entry_type = str(entry.get("type", "")).lower()
            if length_val <= 0:
                if entry_type in ("bitfield", "bool", "boolean", "combo"):
                    length_val = size_val
                elif entry_type in ("number", "slider", "int", "uint", "pointer", "float"):
                    length_val = size_val * 8
            if length_val <= 0:
                continue
            field: dict[str, object] = {
                "name": field_name,
                "offset": hex(offset_val),
                "startBit": int(start_bit),
                "length": int(length_val),
            }
            raw_type = entry.get("type")
            normalized_type = entry.get("type_normalized")
            if raw_type not in (None, ""):
                field["type_raw"] = raw_type
            if normalized_type not in (None, ""):
                field["type_normalized"] = normalized_type
                field["type"] = normalized_type
            elif raw_type not in (None, ""):
                field["type"] = raw_type
            if entry.get("requiresDereference"):
                field["requiresDereference"] = True
                field["dereferenceAddress"] = to_int(entry.get("dereferenceAddress"))
            if "values" in entry and isinstance(entry["values"], list):
                field["values"] = entry["values"]
            try:
                dcat = dropdowns.get(cat_name) or dropdowns.get(cat_name.title()) or {}
                if field_name in dcat and isinstance(dcat[field_name], list):
                    field.setdefault("values", list(dcat[field_name]))
                elif field_name.upper().startswith("PLAYTYPE") and isinstance(dcat.get("PLAYTYPE"), list):
                    field.setdefault("values", list(dcat["PLAYTYPE"]))
            except Exception:
                pass
            _finalize_field_metadata(
                field,
                cat_name,
                offset_val=offset_val,
                start_bit_val=start_bit,
                length_val=length_val,
                source_entry=entry,
            )
            categories.setdefault(cat_name, []).append(field)
        if categories:
            base_categories = {key: list(value) for key, value in categories.items()}
            for cat_name, fields in base_categories.items():
                seen = seen_fields_global.setdefault(cat_name, set())
                for field in fields:
                    if not isinstance(field, dict):
                        continue
                    seen.add(str(field.get("name", "")))
                    offset_int = to_int(field.get("offset"))
                    start_val = to_int(field.get("startBit") or field.get("start_bit"))
                    length_val = to_int(field.get("length"))
                    key = (cat_name, offset_int)
                    bit_cursor[key] = max(bit_cursor.get(key, 0), start_val + max(length_val, 0))
    if base_categories:
        categories = {key: list(value) for key, value in base_categories.items()}
        if categories:
            _emit_super_type_warnings()
            return categories

    base_dir = Path(__file__).resolve().parent
    project_root = base_dir.parent
    unified_candidates: list[Path] = []
    offsets_dir = project_root / "Offsets"
    offsets_dir_lower = project_root / "offsets"
    try:
        for fname in _derive_offset_candidates(MODULE_NAME):
            for folder in (project_root, offsets_dir, offsets_dir_lower):
                p = folder / fname
                if p.is_file():
                    unified_candidates.append(p)
                    break
    except Exception:
        pass
    if not unified_candidates:
        for fname in UNIFIED_FILES:
            for folder in (project_root, offsets_dir, offsets_dir_lower):
                p = folder / fname
                if p.is_file():
                    unified_candidates.append(p)
                    break
    for upath in unified_candidates:
        try:
            with open(upath, "r", encoding="utf-8") as f:
                udata = json.load(f)
            categories = {key: list(value) for key, value in base_categories.items()}
            for cat_name, fields in categories.items():
                seen = seen_fields_global.setdefault(cat_name, set())
                for field in fields:
                    if not isinstance(field, dict):
                        continue
                    seen.add(str(field.get("name", "")))
                    offset_int = to_int(field.get("offset"))
                    start_val = to_int(field.get("startBit") or field.get("start_bit"))
                    length_val = to_int(field.get("length"))
                    key = (cat_name, offset_int)
                    bit_cursor[key] = max(bit_cursor.get(key, 0), start_val + max(length_val, 0))
            if isinstance(udata, dict):
                for key, value in udata.items():
                    key_lower = key.lower()
                    if key_lower in {"base", "offsets", "game_info", "base_pointers"}:
                        continue
                    if isinstance(value, list) and all(isinstance(x, dict) for x in value):
                        normalized_fields: list[dict] = []
                        seen = seen_fields_global.setdefault(key, set())
                        for entry in value:
                            if not isinstance(entry, dict):
                                continue
                            _register_category_metadata(key, entry)
                            _finalize_field_metadata(
                                entry,
                                key,
                                source_entry=entry,
                            )
                            normalized_fields.append(entry)
                            seen.add(str(entry.get("name", "")))
                            offset_int = to_int(entry.get("offset"))
                            start_val = to_int(entry.get("startBit") or entry.get("start_bit"))
                            length_val = to_int(entry.get("length"))
                            bit_cursor[(key, offset_int)] = max(
                                bit_cursor.get((key, offset_int), 0),
                                start_val + max(length_val, 0),
                            )
                        categories[key] = normalized_fields
                pinf = udata.get("Player_Info")
                if isinstance(pinf, dict):
                    new_cats: dict[str, list[dict]] = {}

                    def _append_field(cat_label: str, field_name: str, prefix: str | None, fdef: dict) -> None:
                        display_name = field_name if prefix in (None, "") else f"{prefix} - {field_name}"
                        off_raw = fdef.get("address") or fdef.get("offset_from_base") or fdef.get("offset")
                        offset_int = to_int(off_raw)
                        if offset_int < 0:
                            return
                        f_type = str(fdef.get("type", "")).lower()
                        start_raw = fdef.get("startBit") or fdef.get("start_bit") or fdef.get("bit_start")
                        explicit_start = start_raw is not None
                        start_bit_local = to_int(start_raw)
                        size_int = to_int(fdef.get("size"))
                        length_int = to_int(fdef.get("length"))
                        if length_int <= 0:
                            if f_type in ("bitfield", "bool", "boolean", "combo"):
                                length_int = size_int
                            elif f_type in ("number", "slider", "int", "uint", "pointer"):
                                length_int = size_int * 8
                            elif f_type == "float":
                                length_int = 32 if size_int <= 0 else size_int * 8
                        if length_int <= 0:
                            return
                        if f_type in ("bitfield", "bool", "boolean", "combo") and not explicit_start:
                            key_local = (cat_label, offset_int)
                            start_bit_local = bit_cursor.get(key_local, 0)
                            bit_cursor[key_local] = start_bit_local + length_int
                        entry_local: dict[str, object] = {
                            "name": display_name,
                            "offset": hex(offset_int),
                            "startBit": int(start_bit_local),
                            "length": int(length_int),
                        }
                        if f_type:
                            entry_local["type"] = f_type
                        if f_type == "combo":
                            try:
                                value_count = min(1 << length_int, 64)
                                entry_local["values"] = [str(i) for i in range(max(value_count, 0))]
                            except Exception:
                                pass
                        try:
                            dcat = dropdowns.get(cat_label) or dropdowns.get(cat_label.title()) or {}
                            if display_name in dcat and isinstance(dcat[display_name], list):
                                entry_local.setdefault("values", list(dcat[display_name]))
                            elif field_name.upper().startswith("PLAYTYPE") and isinstance(dcat.get("PLAYTYPE"), list):
                                entry_local.setdefault("values", list(dcat["PLAYTYPE"]))
                        except Exception:
                            pass
                        seen_set = seen_fields_global.setdefault(cat_label, set())
                        if display_name in seen_set:
                            return
                        seen_set.add(display_name)
                        bit_cursor[(cat_label, offset_int)] = max(
                            bit_cursor.get((cat_label, offset_int), 0),
                            start_bit_local + length_int,
                        )
                        _finalize_field_metadata(
                            entry_local,
                            cat_label,
                            offset_val=offset_int,
                            start_bit_val=start_bit_local,
                            length_val=length_int,
                            source_entry=fdef,
                        )
                        new_cats.setdefault(cat_label, []).append(entry_local)

                    def _walk_field_map(base_label: str, mapping: dict, prefix: str | None = None) -> None:
                        for fname, fdef in mapping.items():
                            if not isinstance(fdef, dict):
                                continue
                            has_direct_keys = any(
                                key_local in fdef
                                for key_local in (
                                    "address",
                                    "offset_from_base",
                                    "offset",
                                    "startBit",
                                    "start_bit",
                                    "bit_start",
                                    "size",
                                    "length",
                                    "type",
                                )
                        )
                            if has_direct_keys:
                                cat_label_local = base_label
                                _append_field(cat_label_local, fname, prefix, fdef)
                            else:
                                next_prefix = fname if prefix is None else f"{prefix} - {fname}"
                                _walk_field_map(base_label, fdef, next_prefix)

                    for cat_key, field_map in pinf.items():
                        if not isinstance(field_map, dict):
                            continue
                        cat_name = cat_key[:-8] if cat_key.endswith("_offsets") else cat_key
                        cat_name = cat_name.title()
                        _register_category_metadata(cat_name, {"super_type": super_type_map.get(cat_name.lower())})
                        _walk_field_map(cat_name, field_map)
                    if new_cats:
                        for key_local, vals in new_cats.items():
                            if key_local in categories:
                                categories[key_local].extend(vals)
                            else:
                                categories[key_local] = vals
                if categories:
                    _emit_super_type_warnings()
                    return categories
        except Exception:
            pass
    if base_categories:
        categories = {key: list(value) for key, value in base_categories.items()}
        if categories:
            _emit_super_type_warnings()
            return categories
    return {}


def _normalize_chain_steps(chain_data: object) -> list[dict[str, object]]:
    steps: list[dict[str, object]] = []
    if not isinstance(chain_data, list):
        return steps
    for hop in chain_data:
        if isinstance(hop, dict):
            offset = to_int(
                hop.get("offset")
                or hop.get("add")
                or hop.get("delta")
                or hop.get("value")
                or hop.get("rva")
            )
            post_add = to_int(
                hop.get("post")
                or hop.get("postAdd")
                or hop.get("post_add")
                or hop.get("finalOffset")
                or hop.get("final_offset")
            )
            deref = False
            for key in ("dereference", "deref", "read", "pointer", "follow", "resolve", "resolvePointer", "resolve_pointer"):
                if hop.get(key):
                    deref = True
                    break
            hop_type = str(hop.get("type", "")).lower()
            if hop_type in {"read", "pointer", "deref"}:
                deref = True
            steps.append({
                "offset": offset,
                "post_add": post_add,
                "dereference": deref,
            })
        else:
            steps.append({
                "offset": to_int(hop),
                "post_add": 0,
                "dereference": True,
            })
    return steps


def _parse_pointer_chain_config(base_cfg: dict | None) -> list[dict[str, object]]:
    chains: list[dict[str, object]] = []
    if not isinstance(base_cfg, dict):
        return chains
    addr_raw = base_cfg.get("address")
    if addr_raw is None:
        addr_raw = base_cfg.get("rva")
    if addr_raw is None:
        addr_raw = base_cfg.get("base")
    if addr_raw is None:
        return chains
    base_addr = to_int(addr_raw)
    final_offset = to_int(base_cfg.get("finalOffset") or base_cfg.get("final_offset"))
    absolute_flag = base_cfg.get("absolute")
    if absolute_flag is None:
        absolute_flag = base_cfg.get("isAbsolute")
    is_absolute = bool(absolute_flag)
    direct_table = bool(
        base_cfg.get("direct_table")
        or base_cfg.get("direct")
        or base_cfg.get("directTable")
        or base_cfg.get("treat_as_base")
    )
    chain_data = base_cfg.get("chain") or base_cfg.get("steps")
    if isinstance(chain_data, list) and chain_data:
        candidate_like = [
            item for item in chain_data
            if isinstance(item, dict) and any(key in item for key in ("address", "rva", "base"))
        ]
        if candidate_like and len(candidate_like) == len(chain_data):
            for candidate in chain_data:
                candidate_addr = candidate.get("address")
                if candidate_addr is None:
                    candidate_addr = candidate.get("rva", candidate.get("base"))
                candidate_absolute = candidate.get("absolute")
                if candidate_absolute is None:
                    candidate_absolute = candidate.get("isAbsolute")
                chains.extend(_parse_pointer_chain_config({
                    "address": candidate_addr if candidate_addr is not None else base_addr,
                    "chain": candidate.get("chain") or candidate.get("steps"),
                    "finalOffset": candidate.get("finalOffset") or candidate.get("final_offset") or final_offset,
                    "absolute": candidate_absolute if candidate_absolute is not None else is_absolute,
                    "direct_table": candidate.get("direct_table") or candidate.get("direct"),
                }))
        if chains:
            return chains
    steps = _normalize_chain_steps(chain_data)
    chains.append({
        "rva": base_addr,
        "steps": steps,
        "final_offset": final_offset,
        "absolute": is_absolute,
        "direct_table": direct_table,
    })
    return chains


def _extend_pointer_candidates(target: list[dict[str, object]], candidates: object) -> None:
    """Append pointer chain candidates defined using legacy tuple/dict notation."""
    if not isinstance(candidates, (list, tuple)):
        return
    for candidate in candidates:
        candidate_cfg: dict[str, object] | None = None
        if isinstance(candidate, dict):
            candidate_cfg = dict(candidate)
        elif isinstance(candidate, (list, tuple)):
            if not candidate:
                continue
            rva = to_int(candidate[0])
            if rva == 0:
                continue
            final_offset = to_int(candidate[1]) if len(candidate) > 1 else 0
            extra_deref = bool(candidate[2]) if len(candidate) > 2 else False
            direct_table = bool(candidate[3]) if len(candidate) > 3 else False
            candidate_cfg = {
                "address": rva,
                "absolute": False,
                "finalOffset": final_offset,
            }
            steps: list[dict[str, object]] = []
            if extra_deref:
                steps.append({"offset": 0, "dereference": True})
            if steps:
                candidate_cfg["steps"] = steps
            if direct_table:
                candidate_cfg["direct_table"] = True
        else:
            continue
        if not isinstance(candidate_cfg, dict):
            continue
        chains = _parse_pointer_chain_config(candidate_cfg)
        if chains:
            target.extend(chains)


def _normalize_base_pointer_overrides(overrides: dict[str, int] | None) -> dict[str, int]:
    if not overrides:
        return {}
    normalized: dict[str, int] = {}
    allowed_keys = set(BASE_POINTER_SIZE_KEY_MAP.keys())
    for raw_key, raw_value in overrides.items():
        addr = to_int(raw_value)
        if addr is None or addr <= 0:
            continue
        label = str(raw_key or "").strip()
        if not label or label not in allowed_keys:
            continue
        normalized[label] = addr
    return normalized


def _apply_base_pointer_overrides(data: dict, overrides: dict[str, int]) -> None:
    """Merge dynamic base overrides into an offsets payload."""
    if not overrides or not isinstance(data, dict):
        return

    def _merge(target: object) -> dict[str, object]:
        base_map = target if isinstance(target, dict) else {}
        merged = dict(base_map)
        for key, addr in overrides.items():
            merged[key] = {"address": addr, "absolute": True, "direct_table": True, "finalOffset": 0}
        return merged

    data["base_pointers"] = _merge(data.get("base_pointers"))
    versions = data.get("versions")
    if isinstance(versions, dict):
        for vinfo in versions.values():
            if not isinstance(vinfo, dict):
                continue
            vinfo["base_pointers"] = _merge(vinfo.get("base_pointers"))


def _apply_offset_config(data: dict | None) -> None:
    """Update module-level constants using the loaded offset data."""
    global MODULE_NAME, PLAYER_TABLE_RVA, PLAYER_STRIDE
    global PLAYER_PTR_CHAINS, OFF_LAST_NAME, OFF_FIRST_NAME
    global OFF_TEAM_PTR, OFF_TEAM_ID, OFF_TEAM_NAME, NAME_MAX_CHARS
    global FIRST_NAME_ENCODING, LAST_NAME_ENCODING, TEAM_NAME_ENCODING
    global TEAM_STRIDE, TEAM_NAME_OFFSET, TEAM_NAME_LENGTH, TEAM_PLAYER_SLOT_COUNT
    global TEAM_PTR_CHAINS, TEAM_RECORD_SIZE, TEAM_FIELD_DEFS
    global STAFF_STRIDE, STAFF_RECORD_SIZE, STAFF_PTR_CHAINS, STAFF_NAME_OFFSET, STAFF_NAME_LENGTH, STAFF_NAME_ENCODING
    global STADIUM_STRIDE, STADIUM_RECORD_SIZE, STADIUM_PTR_CHAINS, STADIUM_NAME_OFFSET, STADIUM_NAME_LENGTH, STADIUM_NAME_ENCODING
    if not data:
        raise OffsetSchemaError(f"{OFFSETS_BUNDLE_FILE} is missing or empty.")
    _version_label, base_pointers, game_info = _resolve_version_context(
        cast(dict[str, Any], data),
        _current_offset_target or MODULE_NAME,
    )
    combined_offsets: list[dict] = []
    offsets = data.get("offsets")
    if isinstance(offsets, list):
        combined_offsets.extend(item for item in offsets if isinstance(item, dict))
    if not combined_offsets:
        _offset_index.clear()
        _offset_normalized_index.clear()
        raise OffsetSchemaError(f"No offsets defined in {OFFSETS_BUNDLE_FILE}.")
    _build_offset_index(combined_offsets)

    errors: list[str] = []
    warnings: list[str] = []

    module_candidate = game_info.get("executable")
    if module_candidate:
        MODULE_NAME = str(module_candidate)

    def _pointer_address(defn: dict | None) -> tuple[int, bool]:
        if not isinstance(defn, dict):
            return 0, False
        for key in ("address", "rva", "base"):
            if key in defn:
                return to_int(defn.get(key)), True
        return 0, False

    # Validate base pointers and mapped game_info size keys using exact keys only.
    for key_name in REQUIRED_LIVE_BASE_POINTER_KEYS:
        entry = base_pointers.get(key_name)
        if not isinstance(entry, dict):
            errors.append(f"Missing required base pointer '{key_name}'.")
            continue
        addr_val, has_addr = _pointer_address(entry)
        if not has_addr:
            errors.append(f"Base pointer '{key_name}' is missing an address/rva/base value.")
            continue
        if addr_val <= 0:
            errors.append(f"Base pointer '{key_name}' address must be > 0.")
    for pointer_key, size_key in BASE_POINTER_SIZE_KEY_MAP.items():
        if pointer_key not in base_pointers:
            continue
        entry = base_pointers.get(pointer_key)
        if not isinstance(entry, dict):
            errors.append(f"Base pointer '{pointer_key}' must be an object.")
            continue
        if size_key is None:
            continue
        size_val = to_int(game_info.get(size_key))
        if size_val <= 0:
            errors.append(f"Missing or invalid game_info '{size_key}' for base pointer '{pointer_key}'.")

    PLAYER_STRIDE = max(0, to_int(game_info.get("playerSize")) or 0)
    TEAM_STRIDE = max(0, to_int(game_info.get("teamSize")) or 0)
    STAFF_STRIDE = max(0, to_int(game_info.get("staffSize")) or 0)
    STADIUM_STRIDE = max(0, to_int(game_info.get("stadiumSize")) or 0)
    TEAM_RECORD_SIZE = TEAM_STRIDE
    STAFF_RECORD_SIZE = STAFF_STRIDE
    STADIUM_RECORD_SIZE = STADIUM_STRIDE

    PLAYER_PTR_CHAINS.clear()
    player_base = base_pointers.get("Player")
    player_addr, player_addr_defined = _pointer_address(player_base if isinstance(player_base, dict) else None)
    if player_addr_defined:
        PLAYER_TABLE_RVA = player_addr
        player_chains = _parse_pointer_chain_config(player_base)
        if player_chains:
            PLAYER_PTR_CHAINS.extend(player_chains)
        else:
            errors.append("Player base pointer chain produced no resolvable entries.")
    else:
        PLAYER_TABLE_RVA = 0

    TEAM_PTR_CHAINS.clear()
    team_base = base_pointers.get("Team")
    team_addr, team_addr_defined = _pointer_address(team_base if isinstance(team_base, dict) else None)
    global TEAM_TABLE_RVA
    TEAM_TABLE_RVA = team_addr if team_addr_defined else 0
    if team_addr_defined:
        team_chains = _parse_pointer_chain_config(team_base)
        if team_chains:
            TEAM_PTR_CHAINS.extend(team_chains)
        else:
            errors.append("Team base pointer chain produced no resolvable entries.")

    DRAFT_PTR_CHAINS.clear()
    draft_entry = base_pointers.get("DraftClass")
    if isinstance(draft_entry, dict):
        draft_chains = _parse_pointer_chain_config(draft_entry)
        if draft_chains:
            DRAFT_PTR_CHAINS.extend(draft_chains)

    pointer_candidates = data.get("pointer_candidates")
    if isinstance(pointer_candidates, dict):
        extra_player_candidates = pointer_candidates.get("Player")
        if extra_player_candidates:
            _extend_pointer_candidates(PLAYER_PTR_CHAINS, extra_player_candidates)
        extra_team_candidates = pointer_candidates.get("Team")
        if extra_team_candidates:
            _extend_pointer_candidates(TEAM_PTR_CHAINS, extra_team_candidates)
        extra_draft_candidates = pointer_candidates.get("DraftClass")
        if extra_draft_candidates:
            _extend_pointer_candidates(DRAFT_PTR_CHAINS, extra_draft_candidates)
        extra_staff_candidates = pointer_candidates.get("Staff")
        if extra_staff_candidates:
            _extend_pointer_candidates(STAFF_PTR_CHAINS, extra_staff_candidates)
        extra_stadium_candidates = pointer_candidates.get("Stadium")
        if extra_stadium_candidates:
            _extend_pointer_candidates(STADIUM_PTR_CHAINS, extra_stadium_candidates)

    def _require_field(key_name: str) -> dict | None:
        cat_name, norm_name = STRICT_OFFSET_FIELD_KEYS[key_name]
        entry = _find_offset_entry_by_normalized(cat_name, norm_name)
        if not isinstance(entry, dict):
            errors.append(f"Missing required offset field '{cat_name}/{norm_name}'.")
            return None
        return entry

    first_entry = _require_field("player_first_name")
    OFF_FIRST_NAME = to_int(first_entry.get("address")) if isinstance(first_entry, dict) else 0
    if OFF_FIRST_NAME < 0:
        errors.append("Vitals/FIRSTNAME address must be >= 0.")
        OFF_FIRST_NAME = 0
    FIRST_NAME_ENCODING = "ascii" if str((first_entry or {}).get("type", "")).lower() in ("string", "text") else "utf16"
    first_len = to_int((first_entry or {}).get("length"))
    if first_len <= 0:
        errors.append("Vitals/FIRSTNAME length must be > 0.")

    last_entry = _require_field("player_last_name")
    OFF_LAST_NAME = to_int(last_entry.get("address")) if isinstance(last_entry, dict) else 0
    if OFF_LAST_NAME < 0:
        errors.append("Vitals/LASTNAME address must be >= 0.")
        OFF_LAST_NAME = 0
    LAST_NAME_ENCODING = "ascii" if str((last_entry or {}).get("type", "")).lower() in ("string", "text") else "utf16"
    last_len = to_int((last_entry or {}).get("length"))
    if last_len <= 0:
        errors.append("Vitals/LASTNAME length must be > 0.")
    if first_len > 0 or last_len > 0:
        NAME_MAX_CHARS = max(first_len or 0, last_len or 0)

    team_entry = _require_field("player_current_team")
    OFF_TEAM_PTR = to_int(
        (team_entry or {}).get("dereferenceAddress")
        or (team_entry or {}).get("deref_offset")
        or (team_entry or {}).get("dereference_address")
    )
    if OFF_TEAM_PTR < 0:
        errors.append("Vitals/CURRENTTEAM dereference address must be >= 0.")
        OFF_TEAM_PTR = 0
    OFF_TEAM_ID = to_int((team_entry or {}).get("address")) or 0
    if OFF_TEAM_ID <= 0:
        errors.append("Vitals/CURRENTTEAM address must be > 0.")

    team_name_entry = _require_field("team_name")
    TEAM_NAME_OFFSET = to_int((team_name_entry or {}).get("address")) or 0
    if TEAM_NAME_OFFSET < 0:
        errors.append("Team Vitals/TEAMNAME address must be >= 0.")
        TEAM_NAME_OFFSET = 0
    team_name_type = str((team_name_entry or {}).get("type", "")).lower()
    TEAM_NAME_ENCODING = "ascii" if team_name_type in ("string", "text") else "utf16"
    TEAM_NAME_LENGTH = to_int((team_name_entry or {}).get("length")) or 0
    if TEAM_NAME_LENGTH <= 0:
        errors.append("Team Vitals/TEAMNAME length must be > 0.")
    OFF_TEAM_NAME = TEAM_NAME_OFFSET

    team_player_entries = [
        entry
        for entry in combined_offsets
        if str(entry.get("canonical_category", "")) == "Team Players"
    ]
    if team_player_entries:
        TEAM_PLAYER_SLOT_COUNT = len(team_player_entries)
    TEAM_FIELD_DEFS.clear()
    for label, canonical_category, normalized_name in TEAM_FIELD_SPECS:
        entry_obj = _find_offset_entry_by_normalized(canonical_category, normalized_name)
        if not isinstance(entry_obj, dict):
            continue
        offset = to_int(entry_obj.get("address"))
        length_val = to_int(entry_obj.get("length"))
        entry_type = str(entry_obj.get("type", "")).lower()
        if offset <= 0 or length_val <= 0:
            continue
        if entry_type not in ("wstring", "string", "text"):
            continue
        encoding = "ascii" if entry_type in ("string", "text") else "utf16"
        TEAM_FIELD_DEFS[label] = (offset, length_val, encoding)

    STAFF_PTR_CHAINS.clear()
    staff_base = base_pointers.get("Staff")
    staff_addr, staff_addr_defined = _pointer_address(staff_base if isinstance(staff_base, dict) else None)
    if staff_addr_defined:
        staff_chains = _parse_pointer_chain_config(staff_base)
        if staff_chains:
            STAFF_PTR_CHAINS.extend(staff_chains)
        else:
            errors.append("Staff base pointer chain produced no resolvable entries.")

    staff_first_entry = _require_field("staff_first_name")
    staff_last_entry = _require_field("staff_last_name")
    STAFF_NAME_OFFSET = to_int((staff_first_entry or {}).get("address")) or 0
    STAFF_NAME_ENCODING = "ascii" if str((staff_first_entry or {}).get("type", "")).lower() in ("string", "text") else "utf16"
    STAFF_NAME_LENGTH = to_int((staff_first_entry or {}).get("length")) or 0
    if STAFF_NAME_LENGTH <= 0:
        errors.append("Staff Vitals/FIRSTNAME length must be > 0.")
    if isinstance(staff_last_entry, dict):
        last_staff_len = to_int(staff_last_entry.get("length"))
        if last_staff_len <= 0:
            errors.append("Staff Vitals/LASTNAME length must be > 0.")

    STADIUM_PTR_CHAINS.clear()
    stadium_base = base_pointers.get("Stadium")
    stadium_addr, stadium_addr_defined = _pointer_address(stadium_base if isinstance(stadium_base, dict) else None)
    if stadium_addr_defined:
        stadium_chains = _parse_pointer_chain_config(stadium_base)
        if stadium_chains:
            STADIUM_PTR_CHAINS.extend(stadium_chains)
        else:
            errors.append("Stadium base pointer chain produced no resolvable entries.")

    stadium_name_entry = _require_field("stadium_name")
    STADIUM_NAME_OFFSET = to_int((stadium_name_entry or {}).get("address")) or 0
    if STADIUM_NAME_OFFSET < 0:
        errors.append("Stadium/ARENANAME address must be >= 0.")
        STADIUM_NAME_OFFSET = 0
    STADIUM_NAME_ENCODING = "ascii" if str((stadium_name_entry or {}).get("type", "")).lower() in ("string", "text") else "utf16"
    STADIUM_NAME_LENGTH = to_int((stadium_name_entry or {}).get("length")) or 0
    if STADIUM_NAME_LENGTH <= 0:
        errors.append("Stadium/ARENANAME length must be > 0.")
    if errors:
        raise OffsetSchemaError(" ; ".join(errors))
    if warnings:
        warning_text = " ; ".join(dict.fromkeys(warnings))
        print(f"Offset warnings: {warning_text}")


def initialize_offsets(
    target_executable: str | None = None,
    force: bool = False,
    base_pointer_overrides: dict[str, int] | None = None,
    filename: str | None = None,
) -> None:
    """Ensure offset data for the requested executable is loaded."""
    global _offset_file_path, _offset_config, MODULE_NAME, _current_offset_target, _base_pointer_overrides
    with timed("offsets.initialize_offsets"):
        target_exec = target_executable or MODULE_NAME
        target_key = target_exec.lower()
        overrides_norm = _normalize_base_pointer_overrides(base_pointer_overrides)
        if overrides_norm:
            _base_pointer_overrides = overrides_norm
        elif _base_pointer_overrides:
            overrides_norm = dict(_base_pointer_overrides)
        if force:
            _OFFSET_CACHE.invalidate_target(target_key)
        if _offset_config is not None and not force and _current_offset_target == target_key and not filename:
            MODULE_NAME = target_exec
            if overrides_norm:
                _apply_base_pointer_overrides(_offset_config, overrides_norm)
                _apply_offset_config(_offset_config)
            _sync_player_stats_relations(_offset_config)
            return
        if filename:
            path = Path(filename)
            try:
                with path.open("r", encoding="utf-8") as fh:
                    raw = json.load(fh)
            except Exception as exc:
                raise OffsetSchemaError(f"Failed to load offsets file '{filename}': {exc}") from exc
            resolver = OffsetResolver(
                convert_schema=_convert_merged_offsets_schema,
                select_entry=_select_merged_offset_entry,
            )
            try:
                data = resolver.require_dict(raw, target_exec)
            except OffsetResolveError as exc:
                raise OffsetSchemaError(str(exc)) from exc
        else:
            path, data = _load_offset_config_file(target_exec)
        if not isinstance(data, dict):
            raise OffsetSchemaError(
                f"Unable to locate offset schema for {target_exec}. Expected {SPLIT_OFFSETS_LEAGUE_FILE} and "
                f"{', '.join(SPLIT_OFFSETS_DOMAIN_FILES)} in the Offsets folder."
            )
        if overrides_norm:
            _apply_base_pointer_overrides(data, overrides_norm)
        _offset_file_path = path
        _offset_config = data
        MODULE_NAME = target_exec
        _apply_offset_config(data)
        _sync_player_stats_relations(data)
        MODULE_NAME = target_exec
        _current_offset_target = target_key


__all__ = [
    "OffsetSchemaError",
    "initialize_offsets",
    "BASE_POINTER_SIZE_KEY_MAP",
    "REQUIRED_LIVE_BASE_POINTER_KEYS",
    "STRICT_OFFSET_FIELD_KEYS",
    "CATEGORY_SUPER_TYPES",
    "PLAYER_STATS_RELATIONS",
    "PLAYER_TABLE_RVA",
    "PLAYER_STRIDE",
    "PLAYER_PTR_CHAINS",
    "DRAFT_PTR_CHAINS",
    "DRAFT_CLASS_TEAM_ID",
    "OFF_LAST_NAME",
    "OFF_FIRST_NAME",
    "OFF_TEAM_PTR",
    "OFF_TEAM_NAME",
    "OFF_TEAM_ID",
    "MAX_PLAYERS",
    "MAX_DRAFT_PLAYERS",
    "MAX_TEAMS_SCAN",
    "NAME_MAX_CHARS",
    "FIRST_NAME_ENCODING",
    "LAST_NAME_ENCODING",
    "TEAM_NAME_ENCODING",
    "TEAM_STRIDE",
    "TEAM_NAME_OFFSET",
    "TEAM_NAME_LENGTH",
    "TEAM_PLAYER_SLOT_COUNT",
    "TEAM_PTR_CHAINS",
    "TEAM_TABLE_RVA",
    "TEAM_FIELD_DEFS",
    "TEAM_RECORD_SIZE",
    "TEAM_FIELD_SPECS",
    "PLAYER_PANEL_FIELDS",
    "PLAYER_PANEL_OVR_FIELD",
    "UNIFIED_FILES",
    "EXTRA_CATEGORY_FIELDS",
    "STAFF_STRIDE",
    "STAFF_PTR_CHAINS",
    "STAFF_RECORD_SIZE",
    "STAFF_NAME_OFFSET",
    "STAFF_NAME_LENGTH",
    "STAFF_NAME_ENCODING",
    "MAX_STAFF_SCAN",
    "STADIUM_STRIDE",
    "STADIUM_PTR_CHAINS",
    "STADIUM_RECORD_SIZE",
    "STADIUM_NAME_OFFSET",
    "STADIUM_NAME_LENGTH",
    "STADIUM_NAME_ENCODING",
    "MAX_STADIUM_SCAN",
    "ATTR_IMPORT_ORDER",
    "DUR_IMPORT_ORDER",
    "POTENTIAL_IMPORT_ORDER",
    "TEND_IMPORT_ORDER",
    "FIELD_NAME_ALIASES",
    "NAME_SYNONYMS",
    "NAME_SUFFIXES",
    "_load_categories",
]
