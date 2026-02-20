from __future__ import annotations

import sys
import types
from typing import Any

# Allow importing full editor modules in environments where Dear PyGui is not installed.
sys.modules.setdefault("dearpygui", types.ModuleType("dearpygui"))
sys.modules.setdefault("dearpygui.dearpygui", types.ModuleType("dearpygui.dearpygui"))

from nba2k26_editor.models.player import Player
from nba2k26_editor.models.schema import FieldMetadata
from nba2k26_editor.ui import full_player_editor as full_player_editor_mod
from nba2k26_editor.ui import full_team_editor as full_team_editor_mod
from nba2k26_editor.ui.full_player_editor import FullPlayerEditor
from nba2k26_editor.ui.full_team_editor import FullTeamEditor


class _DPGStub:
    def __init__(self) -> None:
        self.values: dict[str, object] = {}

    def does_item_exist(self, _item: object) -> bool:
        return True

    def get_value(self, item: object) -> object:
        return self.values.get(str(item), "")

    def set_value(self, item: object, value: object) -> None:
        self.values[str(item)] = value


class _AppStub:
    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []
        self.errors: list[tuple[str, str]] = []

    def show_message(self, title: str, message: str) -> None:
        self.messages.append((title, message))

    def show_error(self, title: str, message: str) -> None:
        self.errors.append((title, message))


class _ModelStub:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self.mem = types.SimpleNamespace(hproc=object())

    def encode_field_value(
        self,
        *,
        entity_type: str,
        entity_index: int,
        category: str,
        field_name: str,
        meta: FieldMetadata,
        display_value: object,
        record_ptr: int | None = None,
    ) -> bool:
        self.calls.append(
            {
                "entity_type": entity_type,
                "entity_index": entity_index,
                "category": category,
                "field_name": field_name,
                "display_value": display_value,
                "record_ptr": record_ptr,
            }
        )
        return True


def test_full_player_editor_saves_only_changed_fields() -> None:
    dpg_stub = _DPGStub()
    full_player_editor_mod.dpg = dpg_stub  # type: ignore[assignment]

    app = _AppStub()
    model = _ModelStub()

    editor = FullPlayerEditor.__new__(FullPlayerEditor)
    editor.app = app
    editor.model = model
    editor.player = Player(index=7, record_ptr=0x1000)
    editor.target_players = [editor.player]
    editor.field_vars = {"Vitals": {"Age": "age_ctrl", "Height": "height_ctrl"}}
    editor.field_meta = {
        ("Vitals", "Age"): FieldMetadata(offset=0, start_bit=0, length=8),
        ("Vitals", "Height"): FieldMetadata(offset=1, start_bit=0, length=8),
    }
    editor.field_source_category = {}
    editor._baseline_values = {}
    editor._unsaved_changes = set()
    editor._season_slot_selector_key = None
    editor._closed = False
    editor._initializing = True
    editor._loading_values = False

    editor._apply_loaded_values({("Vitals", "Age"): 25, ("Vitals", "Height"): 80})
    assert editor._baseline_values[("Vitals", "Age")] == 25
    assert editor._baseline_values[("Vitals", "Height")] == 80

    # Change only Age; Height remains baseline.
    dpg_stub.set_value("age_ctrl", 30)
    editor._save_all()

    assert [(c["category"], c["field_name"]) for c in model.calls] == [("Vitals", "Age")]
    assert editor._baseline_values[("Vitals", "Age")] == 30
    assert editor._baseline_values[("Vitals", "Height")] == 80

    # Saving again without edits should not write anything.
    editor._save_all()
    assert len(model.calls) == 1


def test_full_player_editor_does_not_save_fields_without_baseline() -> None:
    dpg_stub = _DPGStub()
    full_player_editor_mod.dpg = dpg_stub  # type: ignore[assignment]

    app = _AppStub()
    model = _ModelStub()

    editor = FullPlayerEditor.__new__(FullPlayerEditor)
    editor.app = app
    editor.model = model
    editor.player = Player(index=7, record_ptr=0x1000)
    editor.target_players = [editor.player]
    editor.field_vars = {"Vitals": {"Age": "age_ctrl", "Height": "height_ctrl"}}
    editor.field_meta = {
        ("Vitals", "Age"): FieldMetadata(offset=0, start_bit=0, length=8),
        ("Vitals", "Height"): FieldMetadata(offset=1, start_bit=0, length=8),
    }
    editor.field_source_category = {}
    editor._baseline_values = {}
    editor._unsaved_changes = set()
    editor._season_slot_selector_key = None
    editor._closed = False
    editor._initializing = True
    editor._loading_values = False

    # Only Age loads successfully (baseline for Height is missing).
    editor._apply_loaded_values({("Vitals", "Age"): 25})
    assert ("Vitals", "Height") not in editor._baseline_values

    # Change Height to something else; it should not be saved because it lacks baseline.
    dpg_stub.set_value("height_ctrl", 81)
    editor._save_all()
    assert model.calls == []


def test_full_player_editor_multi_target_writes_changed_fields_for_all_targets() -> None:
    dpg_stub = _DPGStub()
    full_player_editor_mod.dpg = dpg_stub  # type: ignore[assignment]

    app = _AppStub()
    model = _ModelStub()

    p1 = Player(index=7, record_ptr=0x1000)
    p2 = Player(index=8, record_ptr=0x2000)

    editor = FullPlayerEditor.__new__(FullPlayerEditor)
    editor.app = app
    editor.model = model
    editor.player = p1
    editor.target_players = [p1, p2]
    editor.field_vars = {"Vitals": {"Age": "age_ctrl"}}
    editor.field_meta = {("Vitals", "Age"): FieldMetadata(offset=0, start_bit=0, length=8)}
    editor.field_source_category = {}
    editor._baseline_values = {}
    editor._unsaved_changes = set()
    editor._season_slot_selector_key = None
    editor._closed = False
    editor._initializing = True
    editor._loading_values = False

    editor._apply_loaded_values({("Vitals", "Age"): 25})
    dpg_stub.set_value("age_ctrl", 30)
    editor._save_all()

    assert [c["entity_index"] for c in model.calls] == [7, 8]
    assert all(c["field_name"] == "Age" for c in model.calls)


def test_full_team_editor_saves_only_changed_fields() -> None:
    dpg_stub = _DPGStub()
    full_team_editor_mod.dpg = dpg_stub  # type: ignore[assignment]

    app = _AppStub()
    model = _ModelStub()

    editor = FullTeamEditor.__new__(FullTeamEditor)
    editor.app = app
    editor.model = model
    editor.team_index = 3
    editor.team_name = "Test Team"
    editor.field_vars = {"Info": {"Name": "name_ctrl", "Abbrev": "abbr_ctrl"}}
    editor.field_meta = {
        ("Info", "Name"): FieldMetadata(offset=0, start_bit=0, length=8),
        ("Info", "Abbrev"): FieldMetadata(offset=1, start_bit=0, length=8),
    }
    editor._baseline_values = {}
    editor._unsaved_changes = set()
    editor._closed = False
    editor._initializing = True
    editor._loading_values = False

    editor._apply_loaded_values({("Info", "Name"): 1, ("Info", "Abbrev"): 2})
    dpg_stub.set_value("abbr_ctrl", 3)
    editor._save_all()

    assert [(c["category"], c["field_name"]) for c in model.calls] == [("Info", "Abbrev")]
    assert editor._baseline_values[("Info", "Abbrev")] == 3

