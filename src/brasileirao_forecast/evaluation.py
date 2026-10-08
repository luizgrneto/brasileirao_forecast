"""Walk-forward evaluation: train on the past, predict the future, never peek."""

from typing import Protocol

import numpy as np
import pandas as pd

from brasileirao_forecast.metrics import PROB_COLUMNS


class Model(Protocol):
    """Anything that can learn from played matches and forecast upcoming ones."""

    def fit(self, history: pd.DataFrame) -> "Model": ...

    def predict(self, matches: pd.DataFrame) -> np.ndarray: ...


def walk_forward_predictions(
    results: pd.DataFrame, model: Model, first_test_season: int
) -> pd.DataFrame:
    """Forecast every match from ``first_test_season`` onwards, one match day at a time.

    For each match day the model is refit using only matches played on earlier days,
    then predicts that day's matches. Matches on the same day never see each other's
    results. Seasons before ``first_test_season`` are used only as history.

    Returns the test matches with ``p_home``, ``p_draw`` and ``p_away`` columns added.
    """
    ordered = results.sort_values("kickoff", kind="stable").reset_index(drop=True)
    day = ordered["kickoff"].dt.normalize()
    test_days = day[ordered["season"] >= first_test_season].unique()

    if len(test_days) == 0:
        raise ValueError(f"no matches from season {first_test_season} onwards")
    if not (day < test_days[0]).any():
        raise ValueError("no history before the first test day; pick a later first_test_season")

    chunks = []
    for test_day in test_days:
        today = ordered[day == test_day].copy()
        model.fit(ordered[day < test_day])
        today[PROB_COLUMNS] = model.predict(today)
        chunks.append(today)
    return pd.concat(chunks, ignore_index=True)


def matches_of(matches: pd.DataFrame, team: str) -> pd.DataFrame:
    """Select the matches a team played, home or away (e.g. the focus team)."""
    return matches[(matches["home_team"] == team) | (matches["away_team"] == team)]
