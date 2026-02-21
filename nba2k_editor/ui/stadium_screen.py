"""Stadium screen for Dear PyGui."""
from __future__ import annotations

import dearpygui.dearpygui as dpg


def build_stadium_screen(app) -> None:
    with dpg.child_window(
        tag="screen_stadium",
        parent=app.content_root,
        autosize_x=True,
        autosize_y=True,
        show=False,
    ) as tag:
        app.screen_tags["stadium"] = tag
        with dpg.group(horizontal=True):
            dpg.add_text("Stadiums", color=(224, 225, 221, 255))
            app.stadium_status_text_tag = dpg.add_text(
                app.stadium_status_var.get(),
                color=(155, 164, 181, 255),
            )
        dpg.add_spacer(height=6)
        with dpg.group(horizontal=True):
            dpg.add_text("Search")
            app.stadium_search_input_tag = dpg.add_input_text(
                hint="Search stadiums.",
                width=240,
                callback=lambda _s, value: _on_search_changed(app, value),
            )
            dpg.add_button(label="Refresh", width=90, callback=app._refresh_stadium_list)
        dpg.add_spacer(height=6)
        with dpg.group(horizontal=True):
            with dpg.child_window(tag="stadium_list_container", width=360, autosize_y=True, border=True) as list_container:
                app.stadium_list_container = list_container
                dpg.add_text("No stadiums loaded.")
            with dpg.child_window(tag="stadium_detail_container", autosize_x=True, autosize_y=True, border=True):
                dpg.add_text("Stadium Details", color=(224, 225, 221, 255))
                app.stadium_count_text_tag = dpg.add_text(
                    app.stadium_count_var.get(),
                    color=(155, 164, 181, 255),
                    wrap=520,
                )
                app.btn_stadium_full = dpg.add_button(
                    label="Open Stadium Editor",
                    width=200,
                    enabled=False,
                    callback=lambda: app._open_full_stadium_editor(app._current_stadium_index()),
                )


def _on_search_changed(app, value: str) -> None:
    app.stadium_search_var.set(value or "")
    app._filter_stadium_list()


__all__ = ["build_stadium_screen"]