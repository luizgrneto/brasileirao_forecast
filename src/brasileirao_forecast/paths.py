"""Filesystem locations shared across the project.

`PROJECT_ROOT` assumes the package is used from a source checkout (the setup
`uv sync` creates), which is how this learning project is meant to run.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DOCS_DIR = PROJECT_ROOT / "docs"
