from __future__ import annotations

from types import SimpleNamespace
from typing import Callable

import pytest

pytest.importorskip("dearpygui.dearpygui")

from nba2k_editor.ui.app import PlayerEditorApp
from nba2k_editor.ui import app as app_mod
from nba2k_editor.ui import excel_screen as excel_screen_mod


class _ContextStub:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        del exc_type, exc, tb
        return False


class _ExcelScreenAppStub:
    def __init__(self) -> None:
        self.import_calls: list[str] = []
        self.export_calls: list[str] = []

    def _import_excel(self, entity_key: str) -> None:
        self.import_calls.append(entity_key)

    def _export_excel(self, entity_key: str) -> None:
        self.export_calls.append(entity_key)


class _ExcelAppStub:
    def __init__(self) -> None:
        self.model = SimpleNamespace(mem=SimpleNamespace(open_process=lambda: True))
        self._excel_export_thread = None
        self.errors: list[tuple[str, str]] = []
        self.infos: list[tuple[str, str]] = []

    def show_error(self, title: str, message: str) -> None:
        self.errors.append((title, message))

    def show_info(self, title: str, message: str) -> None:
        self.infos.append((title, message))


class _DialogAppStub:
    pass


class _VarStub:
    def __init__(self, value: float = 0.0) -> None:
        self.value = value

    def set(self, value: float) -> None:
        self.value = value

    def get(self) -> float:
        return self.value


class _ExportFinishAppStub:
    def __init__(self) -> None:
        self._excel_export_thread = object()
        self._excel_export_queue = object()
        self._excel_export_polling = True
        self._excel_export_entity_label = "Players"
        self.excel_progress_var = _VarStub(0.0)
        self.excel_progress_bar_tag = 999
        self.status_messages: list[str] = []
        self.infos: list[tuple[str, str]] = []
        self.errors: list[tuple[str, str]] = []

    def _reset_excel_progress(self) -> None:
        self.excel_progress_var.set(0.0)

    def _set_excel_status(self, message: str) -> None:
        self.status_messages.append(message)

    def show_info(self, title: str, message: str) -> None:
        self.infos.append((title, message))

    def show_error(self, title: str, message: str) -> None:
        self.errors.append((title, message))


def test_excel_section_callbacks_ignore_user_data(monkeypatch: pytest.MonkeyPatch) -> None:
    import_callbacks: dict[str, Callable[..., object]] = {}
    export_callbacks: dict[str, Callable[..., object]] = {}

    monkeypatch.setattr(excel_screen_mod.dpg, "add_text", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(excel_screen_mod.dpg, "group", lambda **_kwargs: _ContextStub())

    def _fake_add_button(*, label: str, width: int, callback, **_kwargs):
        del width
        if len(import_callbacks) < 4:
            import_callbacks[label] = callback
        else:
            export_callbacks[label] = callback
        return len(import_callbacks) + len(export_callbacks)

    monkeypatch.setattr(excel_screen_mod.dpg, "add_button", _fake_add_button)

    app = _ExcelScreenAppStub()
    excel_screen_mod._add_section(app, title="Import", is_import=True)
    excel_screen_mod._add_section(app, title="Export", is_import=False)

    import_callbacks["Players"]("sender", "app_data", None)
    import_callbacks["Teams"]("sender", "app_data", "ignored")
    import_callbacks["Staff"]("sender", "app_data", {"data": 1})
    import_callbacks["Stadiums"]("sender", "app_data", 42)

    export_callbacks["Players"]("sender", "app_data", None)
    export_callbacks["Teams"]("sender", "app_data", "ignored")
    export_callbacks["Staff"]("sender", "app_data", {"data": 1})
    export_callbacks["Stadiums"]("sender", "app_data", 42)

    assert app.import_calls == ["players", "teams", "staff", "stadiums"]
    assert app.export_calls == ["players", "teams", "staff", "stadiums"]


def test_import_excel_blank_entity_reports_error() -> None:
    app = _ExcelAppStub()

    PlayerEditorApp._import_excel(app, "")  # type: ignore[arg-type]

    assert app.errors == [("Excel Import", "Unknown entity type.")]


def test_export_excel_blank_entity_reports_error() -> None:
    app = _ExcelAppStub()

    PlayerEditorApp._export_excel(app, "")  # type: ignore[arg-type]

    assert app.errors == [("Excel Export", "Unknown entity type.")]


def test_open_file_dialog_uses_add_file_extension_filters(monkeypatch: pytest.MonkeyPatch) -> None:
    dialog_kwargs: dict[str, object] = {}
    extension_calls: list[tuple[str, dict[str, object]]] = []
    deleted: list[int] = []
    selected: list[str] = []

    monkeypatch.setattr(app_mod.dpg, "generate_uuid", lambda: 321)
    monkeypatch.setattr(app_mod.dpg, "does_item_exist", lambda _tag: True)
    monkeypatch.setattr(app_mod.dpg, "delete_item", lambda tag: deleted.append(int(tag)))

    def _fake_add_file_dialog(**kwargs):
        dialog_kwargs.update(kwargs)
        return 321

    def _fake_add_file_extension(ext: str, **kwargs):
        extension_calls.append((ext, dict(kwargs)))

    monkeypatch.setattr(app_mod.dpg, "add_file_dialog", _fake_add_file_dialog)
    monkeypatch.setattr(app_mod.dpg, "add_file_extension", _fake_add_file_extension)

    PlayerEditorApp._open_file_dialog(
        _DialogAppStub(),
        "Select workbook",
        default_path="D:/tmp",
        default_filename="ImportPlayers.xlsx",
        file_types=[("Excel files", ".xlsx"), ("All files", ".*")],
        callback=lambda path: selected.append(path),
        save=True,
    )

    assert "file_types" not in dialog_kwargs
    assert dialog_kwargs.get("directory_selector") is False
    assert [ext for ext, _kwargs in extension_calls] == [".xlsx", ".*"]
    assert [kwargs.get("parent") for _ext, kwargs in extension_calls] == [321, 321]

    on_select = dialog_kwargs.get("callback")
    assert callable(on_select)
    on_select(None, {"file_path_name": "D:/tmp/out.xlsx"})
    assert selected == ["D:/tmp/out.xlsx"]
    assert deleted == [321]


def test_finish_excel_export_success_keeps_completion_visible(monkeypatch: pytest.MonkeyPatch) -> None:
    set_calls: list[tuple[int, float]] = []
    monkeypatch.setattr(app_mod.dpg, "does_item_exist", lambda _tag: True)
    monkeypatch.setattr(app_mod.dpg, "set_value", lambda tag, value: set_calls.append((int(tag), float(value))))

    class _Result:
        def summary_text(self) -> str:
            return "Players export: 12 rows written"

    app = _ExportFinishAppStub()
    PlayerEditorApp._finish_excel_export(app, _Result(), None)  # type: ignore[arg-type]

    assert app._excel_export_thread is None
    assert app._excel_export_queue is None
    assert app._excel_export_polling is False
    assert app.excel_progress_var.get() == 1.0
    assert set_calls == [(999, 1.0)]
    assert app.status_messages[-1] == "Players export complete."
    assert app.errors == []
    assert app.infos == [("Excel Export", "Players export: 12 rows written")]