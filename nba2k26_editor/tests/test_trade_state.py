from __future__ import annotations

from nba2k26_editor.models.player import Player
from nba2k26_editor.ui.state.trade_state import TradeState


def test_trade_state_add_and_package_projection():
    state = TradeState(slot_count=2)
    p = Player(1, "LeBron", "James", "Lakers", 1)
    assert state.add_transaction(p, "Lakers", "Heat")
    slot = state.current_slot()
    packages = slot.packages(["Lakers", "Heat"])
    assert p in packages["Lakers"].outgoing
    assert p in packages["Heat"].incoming


def test_trade_state_prevents_duplicates_and_remove():
    state = TradeState(slot_count=1)
    p = Player(2, "Jayson", "Tatum", "Celtics", 2)
    assert state.add_transaction(p, "Celtics", "Bulls")
    assert not state.add_transaction(p, "Celtics", "Bulls")
    assert state.remove_transaction(0)
    assert not state.current_slot().transactions


def test_trade_state_clear_slot():
    state = TradeState(slot_count=1)
    p = Player(3, "Nikola", "Jokic", "Nuggets", 3)
    state.add_transaction(p, "Nuggets", "Knicks")
    state.clear_slot()
    assert state.current_slot().transactions == []

