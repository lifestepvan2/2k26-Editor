"""Stadium editor built with Dear PyGui."""
from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Any, cast

import dearpygui.dearpygui as dpg

from ..core.conversions import to_int as _to_int
from ..models.schema import FieldMetadata

if TYPE_CHECKING:
    from ..models.data_model import PlayerDataModel


class FullStadiumEditor:
    """Tabbed stadium editor using Dear PyGui."""

    def __init__(self, app, model: "PlayerDataModel", stadium_index: int | None = None) -> None:
        self.app = app
        self.model = model
        self.stadium_index = stadium_index if stadium_index is not None else 0
        self._editor_type = "stadium"
        self._closed = False
        self.field_vars: dict[str, dict[str, int | str]] = {}
        self.field_meta: dict[tuple[str, str], FieldMetadata] = {}
        # Baseline UI-side values loaded from memory. Save should only write fields that
        # were successfully loaded into the editor and whose UI values differ from this baseline.
        self._baseline_values: dict[tuple[str, str], object] = {}
        self._unsaved_changes: set[tuple[str, str]] = set()
        self._initializing = True
        self._loading_values = False

        self.window_tag = dpg.generate_uuid()
        self.tab_bar_tag = dpg.generate_uuid()

        with dpg.window(
            label="Stadium Editor",
            tag=self.window_tag,
            width=780,
            height=620,
            no_collapse=True,
            on_close=self._on_close,
        ):
            dpg.add_text(
                "Live editing will activate once stadium base pointers/stride are defined in offsets.json.",
                wrap=680,
            )
            self._build_tabs()
            dpg.add_separator()
            with dpg.group(horizontal=True):
                dpg.add_button(label="Save", width=100, callback=self._save_all)
                dpg.add_button(label="Close", width=100, callback=self._on_close)

        editors = getattr(self.app, "full_editors", None)
        if isinstance(editors, list):
            editors.append(self)
        else:
            self.app.full_editors = [self]

        self._load_all_values_async()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _build_tabs(self) -> None:
        categories = self.model.get_categories_for_super("Stadiums") or {}
        ordered = sorted(categories.keys())
        if not ordered:
            dpg.add_text("No stadium categories detected in offsets.json.", parent=self.window_tag)
            return
        with dpg.tab_bar(tag=self.tab_bar_tag, parent=self.window_tag):
            for cat in ordered:
                self._build_category_tab(cat, categories.get(cat))

    def _build_category_tab(self, category_name: str, fields_obj: list | None = None) -> None:
        fields = fields_obj if isinstance(fields_obj, list) else self.model.categories.get(category_name, [])
        with dpg.tab(label=category_name, parent=self.tab_bar_tag):
            if not fields:
                dpg.add_text("No fields found for this category.")
                return
            table = dpg.add_table(
                header_row=False,
                resizable=False,
                policy=dpg.mvTable_SizingStretchProp,
                scrollX=False,
                scrollY=False,
            )
            dpg.add_table_column(width_fixed=True, init_width_or_weight=230)
            dpg.add_table_column(init_width_or_weight=1.0)
            for row, field in enumerate(fields):
                if not isinstance(field, dict):
                    continue
                name = field.get("name", f"Field {row}")
                with dpg.table_row(parent=table):
                    dpg.add_text(f"{name}:")
                    control = self._add_field_control(category_name, name, field)
                self.field_vars.setdefault(category_name, {})[name] = control

    def _add_field_control(self, category_name: str, field_name: str, field: dict) -> int | str:
        offset_val = _to_int(field.get("offset"))
        start_bit = _to_int(field.get("startBit", field.get("start_bit", 0)))
        length = _to_int(field.get("length", 8))
        byte_length = _to_int(field.get("size") or field.get("length") or 0)
        field_type = str(field.get("type", "")).lower()
        values_list = field.get("values") if isinstance(field, dict) else None
        requires_deref = bool(field.get("requiresDereference") or field.get("requires_deref"))
        deref_offset = _to_int(field.get("dereferenceAddress") or field.get("deref_offset"))
        is_string = any(tag in field_type for tag in ("string", "text", "wstring", "wide", "utf16", "char"))
        is_float = "float" in field_type
        is_color = any(tag in field_type for tag in ("color", "pointer"))
        max_raw = (1 << length) - 1 if length and length < 31 else 999999

        if values_list:
            items = [str(v) for v in values_list]
            control = dpg.add_combo(
                items=items,
                default_value=items[0] if items else "",
                width=200,
                callback=lambda _s, _a, cat=category_name, fname=field_name: self._mark_unsaved(cat, fname),
            )
            self.field_meta[(category_name, field_name)] = FieldMetadata(
                offset=offset_val,
                start_bit=start_bit,
                length=length,
                requires_deref=requires_deref,
                deref_offset=deref_offset,
                widget=control,
                values=tuple(items),
                data_type=field_type or None,
                byte_length=byte_length,
            )
            return control

        if is_string:
            max_chars = length if length > 0 else byte_length if byte_length > 0 else 64
            control = dpg.add_input_text(
                width=260,
                max_chars=max_chars,
                default_value="",
                callback=lambda _s, _a, cat=category_name, fname=field_name: self._mark_unsaved(cat, fname),
            )
            self.field_meta[(category_name, field_name)] = FieldMetadata(
                offset=offset_val,
                start_bit=start_bit,
                length=max_chars,
                requires_deref=requires_deref,
                deref_offset=deref_offset,
                widget=control,
                data_type=field_type or "string",
                byte_length=byte_length,
            )
            return control

        if is_float:
            control = dpg.add_input_float(
                width=160,
                default_value=0.0,
                format="%.4f",
                callback=lambda _s, _a, cat=category_name, fname=field_name: self._mark_unsaved(cat, fname),
            )
            self.field_meta[(category_name, field_name)] = FieldMetadata(
                offset=offset_val,
                start_bit=start_bit,
                length=length,
                requires_deref=requires_deref,
                deref_offset=deref_offset,
                widget=control,
                data_type=field_type or "float",
                byte_length=byte_length,
            )
            return control

        if is_color:
            control = dpg.add_input_text(
                width=180,
                default_value="",
                callback=lambda _s, _a, cat=category_name, fname=field_name: self._mark_unsaved(cat, fname),
            )
            self.field_meta[(category_name, field_name)] = FieldMetadata(
                offset=offset_val,
                start_bit=start_bit,
                length=length,
                requires_deref=requires_deref,
                deref_offset=deref_offset,
                widget=control,
                data_type=field_type or "pointer",
                byte_length=byte_length,
            )
            return control

        control = dpg.add_input_int(
            width=140,
            default_value=0,
            min_value=0,
            max_value=max_raw,
            min_clamped=True,
            max_clamped=True,
            callback=lambda _s, _a, cat=category_name, fname=field_name: self._mark_unsaved(cat, fname),
        )
        self.field_meta[(category_name, field_name)] = FieldMetadata(
            offset=offset_val,
            start_bit=start_bit,
            length=length,
            requires_deref=requires_deref,
            deref_offset=deref_offset,
            widget=control,
            data_type=field_type or "int",
            byte_length=byte_length,
        )
        return control

    # ------------------------------------------------------------------
    # Data loading / saving
    # ------------------------------------------------------------------
    def _load_all_values_async(self) -> None:
        if self._loading_values:
            return
        self._loading_values = True

        def _worker() -> None:
            try:
                self.model.refresh_stadiums()
            except Exception:
                pass
            values: dict[tuple[str, str], object] = {}
            for category, fields in self.field_vars.items():
                for field_name in fields.keys():
                    meta = self.field_meta.get((category, field_name))
                    if not meta:
                        continue
                    value = self.model.decode_field_value(
                        entity_type="stadium",
                        entity_index=self.stadium_index,
                        category=category,
                        field_name=field_name,
                        meta=meta,
                    )
                    if value is None:
                        continue
                    values[(category, field_name)] = value

            def _apply() -> None:
                if self._closed:
                    return
                self._apply_loaded_values(values)

            try:
                self.app.run_on_ui_thread(_apply)
            except Exception:
                _apply()

        threading.Thread(target=_worker, daemon=True).start()

    def _apply_loaded_values(self, values: dict[tuple[str, str], object]) -> None:
        baseline_map = getattr(self, "_baseline_values", None)
        if not isinstance(baseline_map, dict):
            baseline_map = {}
            self._baseline_values = baseline_map
        for (category, field_name), value in values.items():
            control = self.field_vars.get(category, {}).get(field_name)
            meta = self.field_meta.get((category, field_name))
            if control is None or meta is None or not dpg.does_item_exist(control):
                continue
            if meta.values:
                vals = list(meta.values)
                selection = vals[0] if vals else ""
                if isinstance(value, str) and value in vals:
                    selection = value
                else:
                    try:
                        idx = self._coerce_int(value, default=0)
                        if 0 <= idx < len(vals):
                            selection = vals[idx]
                    except Exception:
                        pass
                dpg.set_value(control, selection)
            else:
                dtype = (meta.data_type or "").lower()
                if any(tag in dtype for tag in ("string", "text", "char", "pointer", "wide")):
                    dpg.set_value(control, "" if value is None else str(value))
                elif "float" in dtype:
                    try:
                        dpg.set_value(control, float(cast(Any, value)))
                    except Exception:
                        pass
                else:
                    try:
                        dpg.set_value(control, _to_int(value))
                    except Exception:
                        pass
            try:
                baseline_map[(category, field_name)] = self._get_ui_value(meta, control)
            except Exception:
                pass
            try:
                self._unsaved_changes.discard((category, field_name))
            except Exception:
                pass
        self._initializing = False
        self._loading_values = False

    def _save_all(self) -> None:
        baseline_map = getattr(self, "_baseline_values", None)
        if not isinstance(baseline_map, dict) or not baseline_map:
            self.app.show_message("Save", "No changes to save.")
            return

        errors: list[str] = []
        changed_keys: list[tuple[str, str]] = []
        for (category, field_name), baseline_value in baseline_map.items():
            control = self.field_vars.get(category, {}).get(field_name)
            meta = self.field_meta.get((category, field_name))
            if control is None or meta is None or not dpg.does_item_exist(control):
                continue
            try:
                ui_value = self._get_ui_value(meta, control)
            except Exception:
                errors.append(f"{category}/{field_name}")
                continue
            if ui_value == baseline_value:
                self._unsaved_changes.discard((category, field_name))
                continue
            changed_keys.append((category, field_name))
            success = self.model.encode_field_value(
                entity_type="stadium",
                entity_index=self.stadium_index,
                category=category,
                field_name=field_name,
                meta=meta,
                display_value=ui_value,
            )
            if success:
                baseline_map[(category, field_name)] = ui_value
                self._unsaved_changes.discard((category, field_name))
            else:
                errors.append(f"{category}/{field_name}")

        if errors:
            self.app.show_error("Stadium Editor", "Failed to save fields:\n" + "\n".join(errors))
        elif not changed_keys:
            self.app.show_message("Save", "No changes to save.")
        else:
            self.app.show_message("Stadium Editor", f"Saved {len(changed_keys)} field(s).")

    def _get_ui_value(self, meta: FieldMetadata, control_tag: int | str) -> object:
        if meta.values:
            selected = dpg.get_value(control_tag)
            values_list = list(meta.values)
            if selected in values_list:
                return values_list.index(selected)
            return 0
        dtype = (meta.data_type or "").lower()
        value = dpg.get_value(control_tag)
        if any(tag in dtype for tag in ("string", "text", "char", "pointer", "wide")):
            return "" if value is None else str(value)
        if "float" in dtype:
            try:
                return float(cast(Any, value))
            except Exception:
                return 0.0
        return _to_int(value)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _mark_unsaved(self, category: str, field_name: str) -> None:
        if self._initializing:
            return
        self._unsaved_changes.add((category, field_name))

    @staticmethod
    def _coerce_int(value: object, default: int = 0) -> int:
        try:
            return int(cast(Any, value))
        except Exception:
            return default

    def _on_close(self, _sender=None, _app_data=None, _user_data=None) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            editors = getattr(self.app, "full_editors", [])
            if isinstance(editors, list):
                try:
                    editors.remove(self)
                except ValueError:
                    pass
        except Exception:
            pass
        if self.window_tag and dpg.does_item_exist(self.window_tag):
            dpg.delete_item(self.window_tag)


__all__ = ["FullStadiumEditor"]
