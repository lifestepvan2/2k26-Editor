from __future__ import annotations

from types import SimpleNamespace

import pytest

pytest.importorskip("dearpygui.dearpygui")

from nba2k_editor.ai import assistant as assistant_mod
from nba2k_editor.ai.assistant import AIAssistantPanel
from nba2k_editor.core.offsets import OffsetSchemaError
from nba2k_editor.ui import app as app_mod
from nba2k_editor.ui.app import PlayerEditorApp


class _CallbackAppStub:
    def __init__(self) -> None:
        self.callbacks: list[callable] = []
        self.ai_persona_choice_var = None

    def run_on_ui_thread(self, func, delay_ms: int = 0) -> None:
        assert delay_ms == 0
        self.callbacks.append(func)


class _AssistantPanelStub:
    def __init__(self) -> None:
        self.app = _CallbackAppStub()
        self.finalized: list[tuple[str, bool]] = []

    def _finalize_request(self, message: str, success: bool) -> None:
        self.finalized.append((message, success))

    def _append_output(self, text: str) -> None:
        pass


class _DynamicScanStub:
    def __init__(self) -> None:
        self.dynamic_scan_in_progress = True
        self.hook_target_var = SimpleNamespace(get=lambda: "NBA2K26.exe")
        self.model = SimpleNamespace(
            mem=SimpleNamespace(
                module_name="NBA2K26.exe",
                pid=111,
                base_addr=0,
                open_process=lambda: True,
            ),
            invalidate_base_cache=lambda: None,
        )
        self.last_dynamic_base_report: dict[str, object] = {}
        self.last_dynamic_base_overrides: dict[str, int] = {}
        self.callbacks: list[callable] = []
        self.errors: list[tuple[str, str]] = []
        self.warnings: list[tuple[str, str]] = []
        self.infos: list[tuple[str, str]] = []
        self.status: str = ""

    def _hook_label_for(self, target_exec: str) -> str:
        return target_exec

    def _set_dynamic_scan_status(self, message: str) -> None:
        self.status = message

    def run_on_ui_thread(self, func, delay_ms: int = 0) -> None:
        assert delay_ms == 0
        self.callbacks.append(func)

    def show_error(self, title: str, message: str) -> None:
        self.errors.append((title, message))

    def show_warning(self, title: str, message: str) -> None:
        self.warnings.append((title, message))

    def show_info(self, title: str, message: str) -> None:
        self.infos.append((title, message))

    def _update_status(self) -> None:
        pass

    def _start_scan(self) -> None:
        pass


def _run_ui_callbacks(callbacks: list[callable]) -> None:
    for func in callbacks:
        func()


def test_ai_panel_deferred_error_callback_preserves_exception_message(monkeypatch: pytest.MonkeyPatch) -> None:
    panel = _AssistantPanelStub()

    def _raise_backend(*_args, **_kwargs):
        raise RuntimeError("backend exploded")

    monkeypatch.setattr(assistant_mod, "invoke_ai_backend", _raise_backend)
    try:
        import nba2k_editor.ai.backend_helpers as backend_helpers
    except Exception:  # pragma: no cover - import guard for optional deps
        backend_helpers = None
    if backend_helpers is not None and hasattr(backend_helpers, "generate_text_async"):
        monkeypatch.delattr(backend_helpers, "generate_text_async")

    AIAssistantPanel._run_ai(
        panel,  # type: ignore[arg-type]
        "hello",
        {
            "mode": "local",
            "local": {
                "backend": "python",
                "python_backend": "llama_cpp",
                "model_path": "dummy-model.bin",
                "max_tokens": 16,
                "temperature": 0.2,
            },
        },
    )
    _run_ui_callbacks(panel.app.callbacks)

    assert panel.finalized == [("AI error: backend exploded", False)]


def test_dynamic_scan_offsets_load_error_callback_survives_exception_scope(monkeypatch: pytest.MonkeyPatch) -> None:
    stub = _DynamicScanStub()

    def _raise_offsets(*_args, **_kwargs):
        raise OffsetSchemaError("offset config invalid")

    monkeypatch.setattr(app_mod, "initialize_offsets", _raise_offsets)

    PlayerEditorApp._run_dynamic_base_scan(stub)  # type: ignore[arg-type]
    _run_ui_callbacks(stub.callbacks)

    assert stub.errors == [("Offsets not loaded", "offset config invalid")]


def test_dynamic_scan_failure_warning_callback_survives_exception_scope(monkeypatch: pytest.MonkeyPatch) -> None:
    stub = _DynamicScanStub()

    monkeypatch.setattr(app_mod, "initialize_offsets", lambda *_args, **_kwargs: None)

    def _raise_scan(*_args, **_kwargs):
        raise RuntimeError("scanner crashed")

    monkeypatch.setattr(app_mod, "find_dynamic_bases", _raise_scan)

    PlayerEditorApp._run_dynamic_base_scan(stub)  # type: ignore[arg-type]
    _run_ui_callbacks(stub.callbacks)

    assert stub.warnings == [("Dynamic base discovery", "Dynamic base scan failed; using offsets file.\nscanner crashed")]


def test_dynamic_apply_failure_warning_callback_survives_exception_scope(monkeypatch: pytest.MonkeyPatch) -> None:
    stub = _DynamicScanStub()

    call_count = {"value": 0}

    def _init_offsets(*_args, **_kwargs):
        call_count["value"] += 1
        if call_count["value"] >= 2:
            raise OffsetSchemaError("apply failed")

    monkeypatch.setattr(app_mod, "initialize_offsets", _init_offsets)
    monkeypatch.setattr(
        app_mod,
        "find_dynamic_bases",
        lambda *_args, **_kwargs: ({"Player": 0x1000, "Team": 0x2000}, {"ok": True}),
    )

    PlayerEditorApp._run_dynamic_base_scan(stub)  # type: ignore[arg-type]
    _run_ui_callbacks(stub.callbacks)

    assert stub.warnings == [("Dynamic base discovery", "Dynamic bases found but failed to apply: apply failed")]
