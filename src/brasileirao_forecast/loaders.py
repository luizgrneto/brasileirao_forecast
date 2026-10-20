"""Loaders for raw data files.

Today this module reads the Brazil file from football-data.co.uk (``new/BRA.csv``).
The raw file is downloaded by hand and kept out of git (see ``docs/sources.md``).

Attributes:
    REQUIRED_COLUMNS: Columns of the source CSV that ``load_results`` needs.
    RESULT_LABELS: Match result labels, in the order used everywhere in the
        project: ``"H"`` (home win), ``"D"`` (draw) and ``"A"`` (away win).
"""

from pathlib import Path

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = ["Season", "Date", "Time", "Home", "Away", "HG", "AG", "Res"]
RESULT_LABELS = ("H", "D", "A")  # home win, draw, away win


def result_from_goals(home_goals: pd.Series, away_goals: pd.Series) -> np.ndarray:
    """Derive the result label of each match from its score.

    Args:
        home_goals: Goals scored by the home team in each match.
        away_goals: Goals scored by the away team, aligned with ``home_goals``.

    Returns:
        An array of labels from ``RESULT_LABELS`` with the same length as the
        inputs: ``"H"`` where the home team scored more, ``"A"`` where the away
        team did, and ``"D"`` for equal scores.

    Examples:
        >>> import pandas as pd
        >>> result_from_goals(pd.Series([2, 1, 0]), pd.Series([0, 1, 3])).tolist()
        ['H', 'D', 'A']
    """
    return np.where(home_goals > away_goals, "H", np.where(home_goals < away_goals, "A", "D"))


def load_results(path: str | Path) -> pd.DataFrame:
    """Load played Série A matches from the football-data.co.uk Brazil CSV.

    Besides reading the file, this function cleans and validates it: it renames
    the columns, parses dates, drops matches without a score and checks that the
    ``Res`` column agrees with the scores.

    Args:
        path: Location of the downloaded ``BRA.csv`` file.

    Returns:
        A DataFrame with one row per played match, sorted by kickoff, and these
        columns:

        * ``season`` (int): Season year.
        * ``kickoff`` (datetime64): Date and time of the match, naive (no time zone).
        * ``home_team`` (str): Home club, named as in the source.
        * ``away_team`` (str): Away club, named as in the source.
        * ``home_goals`` (int): Goals scored by the home team.
        * ``away_goals`` (int): Goals scored by the away team.
        * ``result`` (str): One of ``RESULT_LABELS``.

    Raises:
        FileNotFoundError: If ``path`` does not exist.
        ValueError: If required columns are missing, if ``Res`` disagrees with
            the scores, or if the same match appears twice.

    Note:
        * The file has a UTF-8 byte-order mark and dates as ``dd/mm/yyyy``.
        * Some ``Time`` values carry a leading space, so they are stripped.
        * ``kickoff`` is naive because the file does not state its time zone.
        * Rows without a score are dropped (matches that were not played).
        * Club names are kept exactly as in the source; reconciling them with
          other sources is a separate step.

    Examples:
        >>> from brasileirao_forecast.paths import RAW_DIR
        >>> results = load_results(RAW_DIR / "BRA.csv")  # doctest: +SKIP
        >>> results["result"].value_counts()  # doctest: +SKIP
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
