"""Staff screen for Dear PyGui."""
from __future__ import annotations

import dearpygui.dearpygui as dpg


def build_staff_screen(app) -> None:
    with dpg.child_window(
        tag="screen_staff",
        parent=app.content_root,
        autosize_x=True,
        autosize_y=True,
        show=False,
    ) as tag:
        app.screen_tags["staff"] = tag
        with dpg.group(horizontal=True):
            dpg.add_text("Staff", color=(224, 225, 221, 255))
            app.staff_status_text_tag = dpg.add_text(
                app.staff_status_var.get(),
                color=(155, 164, 181, 255),
            )
        dpg.add_spacer(height=6)
        with dpg.group(horizontal=True):
            dpg.add_text("Search")
            app.staff_search_input_tag = dpg.add_input_text(
                hint="Search staff.",
                width=240,
                callback=lambda _s, value: _on_search_changed(app, value),
            )
            dpg.add_button(label="Refresh", width=90, callback=app._refresh_staff_list)
        dpg.add_spacer(height=6)
        with dpg.group(horizontal=True):
            with dpg.child_window(tag="staff_list_container", width=360, autosize_y=True, border=True) as list_container:
                app.staff_list_container = list_container
                dpg.add_text("No staff loaded.")
            with dpg.child_window(tag="staff_detail_container", autosize_x=True, autosize_y=True, border=True):
                dpg.add_text("Staff Details", color=(224, 225, 221, 255))
                app.staff_count_text_tag = dpg.add_text(
                    app.staff_count_var.get(),
                    color=(155, 164, 181, 255),
                    wrap=520,
                )
                app.btn_staff_full = dpg.add_button(
                    label="Open Staff Editor",
                    width=180,
                    enabled=False,
                    callback=lambda: app._open_full_staff_editor(app._current_staff_index()),
                )


def _on_search_changed(app, value: str) -> None:
    app.staff_search_var.set(value or "")
    app._filter_staff_list()


__all__ = ["build_staff_screen"]