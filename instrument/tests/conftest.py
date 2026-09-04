"""pytest configuration: put `instrument/src` on sys.path so `neurospine`
imports without an editable install. This keeps the test suite runnable in
a fresh venv with `pip install pytest` and nothing else.
"""

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
