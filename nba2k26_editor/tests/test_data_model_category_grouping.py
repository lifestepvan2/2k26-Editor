from __future__ import annotations

from nba2k26_editor.core import offsets as offsets_mod
from nba2k26_editor.models.data_model import PlayerDataModel


def test_get_categories_for_super_groups_player_categories(monkeypatch):
    model = PlayerDataModel.__new__(PlayerDataModel)
    model.categories = {
        "Vitals": [{"name": "First Name"}],
        "Attributes": [{"name": "Inside Shot"}],
        "Team Pointers": [{"name": "Hidden Pointer"}],
        "Staff Bio": [{"name": "Staff Field"}],
    }

    monkeypatch.setattr(
        offsets_mod,
        "CATEGORY_SUPER_TYPES",
        {
            "vitals": "Players",
            "attributes": "Players",
            "team pointers": "Players",
            "staff bio": "Staff",
        },
        raising=False,
    )
    monkeypatch.setattr(
        offsets_mod,
        "CATEGORY_CANONICAL",
        {
            "vitals": "Vitals",
            "attributes": "Attributes",
            "team pointers": "Team Pointers",
            "staff bio": "Staff Bio",
        },
        raising=False,
    )

    grouped = PlayerDataModel.get_categories_for_super(model, "Players")

    assert "Vitals" in grouped
    assert "Attributes" in grouped
    assert "Team Pointers" not in grouped
    assert "Staff Bio" not in grouped
