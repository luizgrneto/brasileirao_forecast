"""Filesystem locations shared across the project.

``PROJECT_ROOT`` assumes the package is used from a source checkout, which is
what ``uv sync`` sets up and how this learning project is meant to run. If the
package were installed as a wheel, the derived paths would point inside
``site-packages`` and be wrong.

Attributes:
    PROJECT_ROOT: Root directory of the repository.
    DATA_DIR: Directory for data files. It is never versioned (see
        ``data/README.md``).
    RAW_DIR: Raw files exactly as downloaded, such as ``BRA.csv``.
    PROCESSED_DIR: Cleaned data (Parquet) ready for analysis and modelling.
    DOCS_DIR: Project documentation.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DOCS_DIR = PROJECT_ROOT / "docs"
