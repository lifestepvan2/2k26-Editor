"""
Root pytest configuration.

Ensures the project root is on sys.path so ``nba2k26_editor`` is importable
when running pytest from this directory without installing the package.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Insert project root as first entry so local source always wins over any
# previously installed versions.
_PROJECT_ROOT = Path(__file__).resolve().parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
