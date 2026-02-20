# Copilot Instructions for NBA2K26 Editor

## Project Overview
- This is a Python/Tkinter live-memory editor for NBA 2K26, attaching to the running game process and using offset-driven schemas for editing players, teams, staff, and stadiums.
- The main package is `nba2k26_editor/`. All core logic, UI, and data models live here. Ignore other top-level folders.

## Key Architecture
- **Entry Points:** Use `run_editor.bat`, `python -m nba2k26_editor.entrypoints.gui`, or `python launch_editor.py` to launch the app.
- **Memory Layer:** Win32 memory access is in `nba2k26_editor/memory/` using raw `ctypes` Win32 APIs — no pymem.
- **Offsets/Data:** All offsets and schema data are in `nba2k26_editor/Offsets/`.
- **UI:** Dear PyGui-based UI in `nba2k26_editor/ui/`, with screens, dialogs, and orchestration. Lazy-loads all non-home screens on first navigation.
- **Models:** Data models and import/export logic in `nba2k26_editor/models/`.
- **Tests:** Regression, perf, and integration tests in `nba2k26_editor/tests/`.

## Developer Workflows
- **Development:** Windows only. Use the provided batch or Python launchers.
- **Packaging:** Build with `pyinstaller NBA2K26Editor.spec`. Output is in `nba2k26_editor/dist/`.
- **Testing:** Tests are in `nba2k26_editor/tests/`. Run with standard Python test runners.
- **Docs:** Each major folder has a `README.md` with architecture and data flow details. Always read these before editing.

## Project Conventions
- **Folder Boundaries:** Each subfolder maintains strict boundaries and runtime behavior. Only cross boundaries via documented interfaces.
- **Data Flow:** Most modules return results/events/state to the UI, model, runtime, or CLI depending on workflow.
- **Offset Discovery:** For memory scanning signatures and pointer layouts, follow `nba2k26_editor/Offsets/AGENTS.md`.
- **Extension Points:** Add custom panels or editor add-ons via the extension hooks in the main package.
- **Dependencies:** Only `dearpygui` is a hard runtime requirement. `psutil` and `openpyxl` are optional (import-guarded). See `requirements.txt`.

## Examples
- To add a new UI screen, create a module in `ui/`, register a builder in `_lazy_screen_builders` and a nav button in `_build_sidebar` inside `app.py`, then follow the lazy-load pattern.
- To update offsets, edit the relevant JSON in `Offsets/` and update any schema logic in `core/` or `models/`.

## References
- Main architecture: `nba2k26_editor/README.md`
- UI: `nba2k26_editor/ui/README.md`
- Offsets: `nba2k26_editor/Offsets/README.md`
- Data models: `nba2k26_editor/models/README.md`
- Tests: `nba2k26_editor/tests/README.md`
- Base discovery (memory scanning): `nba2k26_editor/Offsets/AGENTS.md`

---
For any non-obvious workflow or integration, always check the relevant folder's README and AGENTS.md before making changes.
