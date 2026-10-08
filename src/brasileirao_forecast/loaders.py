"""Loaders for raw data files.

Today this module reads the Brazil file from football-data.co.uk (``new/BRA.csv``).
The raw file is downloaded by hand and kept out of git (see ``docs/sources.md``).
"""

from pathlib import Path

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = ["Season", "Date", "Time", "Home", "Away", "HG", "AG", "Res"]
RESULT_LABELS = ("H", "D", "A")  # home win, draw, away win


def result_from_goals(home_goals: pd.Series, away_goals: pd.Series) -> np.ndarray:
    """Return the match result labels ("H", "D" or "A") implied by the scores."""
    return np.where(home_goals > away_goals, "H", np.where(home_goals < away_goals, "A", "D"))


def load_results(path: str | Path) -> pd.DataFrame:
    """Load played Série A matches from the football-data.co.uk Brazil CSV.

    Returns one row per played match, sorted by kickoff, with columns:
    ``season``, ``kickoff``, ``home_team``, ``away_team``, ``home_goals``,
    ``away_goals`` and ``result`` (one of ``RESULT_LABELS``).

    Notes:
        * The file has a UTF-8 byte-order mark and dates as ``dd/mm/yyyy``.
        * Some ``Time`` values carry a leading space, so they are stripped.
        * ``kickoff`` is naive: the file does not state its time zone.
        * Rows without a score are dropped (matches that were not played).
        * Club names are kept exactly as in the source; reconciling them with
          other sources is a separate step.

    Raises:
        ValueError: if required columns are missing, if ``Res`` disagrees with
            the scores, or if the same match appears twice.
    """
    raw = pd.read_csv(path, encoding="utf-8-sig")

    missing = [column for column in REQUIRED_COLUMNS if column not in raw.columns]
    if missing:
        raise ValueError(f"{path}: missing required columns {missing}")

    matches = pd.DataFrame(
        {
            "season": raw["Season"].astype(int),
            "kickoff": pd.to_datetime(
                raw["Date"].str.strip() + " " + raw["Time"].str.strip(),
                format="%d/%m/%Y %H:%M",
            ),
            "home_team": raw["Home"].str.strip(),
            "away_team": raw["Away"].str.strip(),
            "home_goals": raw["HG"],
            "away_goals": raw["AG"],
            "result": raw["Res"],
        }
    )

    played = matches.dropna(subset=["home_goals", "away_goals"]).copy()
    played["home_goals"] = played["home_goals"].astype(int)
    played["away_goals"] = played["away_goals"].astype(int)

    expected = result_from_goals(played["home_goals"], played["away_goals"])
    mismatched = int((played["result"].to_numpy() != expected).sum())
    if mismatched:
        raise ValueError(f"{path}: {mismatched} rows where Res disagrees with the scores")

    duplicated = int(played.duplicated(["kickoff", "home_team", "away_team"]).sum())
    if duplicated:
        raise ValueError(f"{path}: {duplicated} duplicated matches")

    return played.sort_values("kickoff", kind="stable").reset_index(drop=True)
