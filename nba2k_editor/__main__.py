"""Allow `python -m nba2k_editor` to launch the GUI entrypoint."""
from __future__ import annotations

if __name__ == "__main__":
    try:
        from .entrypoints.gui import main
    except ModuleNotFoundError as exc:
        missing = getattr(exc, "name", "") or "dependency"
        raise SystemExit(
            f"Missing dependency '{missing}'. Install GUI dependencies (for example: pip install dearpygui)."
        ) from exc
    main()
