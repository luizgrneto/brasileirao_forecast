"""Walk-forward evaluation: train on the past, predict the future, never peek.

A model is evaluated the way it would be used in real life: before each match day
it may learn from everything that happened on earlier days, and nothing else.
This avoids information leakage, which would make a model look better than it is.
"""

from typing import Protocol

import numpy as np
import pandas as pd

from brasileirao_forecast.metrics import PROB_COLUMNS


class Model(Protocol):
    """Anything that can learn from played matches and forecast upcoming ones.

    A model only needs two methods, ``fit`` and ``predict``. Any class that has
    them with these signatures works with ``walk_forward_predictions``, without
    inheriting from this protocol. ``FrequencyBaseline`` is an example.
    """

    def fit(self, history: pd.DataFrame) -> "Model":
        """Learn from played matches, discarding anything learned before.

        Args:
            history: Played matches, in the format returned by
                ``brasileirao_forecast.loaders.load_results``.

        Returns:
            The fitted model, usually ``self``.
        """
        ...

    def predict(self, matches: pd.DataFrame) -> np.ndarray:
        """Forecast the result probabilities of the given matches.

        Args:
            matches: The matches to forecast, in the same format as ``history``
                in ``fit`` (the ``result`` values are not available to a model
                in real life and must not be used).

        Returns:
            An array of shape ``(n_matches, 3)`` with the probabilities of home
            win, draw and away win, in the order of ``PROB_COLUMNS``. Each row
            must be non-negative and sum to 1.
        """
        ...


def walk_forward_predictions(
    results: pd.DataFrame, model: Model, first_test_season: int
) -> pd.DataFrame:
    """Forecast every match from ``first_test_season`` onwards, one match day at a time.

    For each match day the model is refit using only matches played on earlier days,
    then predicts that day's matches. Matches on the same day never see each other's
    results. Seasons before ``first_test_season`` are used only as history.

    Args:
        results: Played matches, as returned by
            ``brasileirao_forecast.loaders.load_results``. Needs at least the
            columns ``season`` and ``kickoff``, plus whatever ``model`` uses.
        model: The model to evaluate. It is refit in place once per match day,
            so it is left fitted on the history before the last test day.
        first_test_season: First season to forecast. Earlier seasons only serve as
            training history, so there must be at least one before it.

    Returns:
        The test matches (all columns of ``results``) in kickoff order, with the
        columns ``p_home``, ``p_draw`` and ``p_away`` added.

    Raises:
        ValueError: If there are no matches from ``first_test_season`` onwards,
            or no matches before the first test day to learn from.

    Examples:
        >>> import pandas as pd
        >>> from brasileirao_forecast.baseline import FrequencyBaseline
        >>> results = pd.DataFrame(
        ...     {
        ...         "season": [2020, 2021],
        ...         "kickoff": pd.to_datetime(["2020-05-01 20:00", "2021-05-01 20:00"]),
        ...         "home_team": ["A", "A"],
        ...         "away_team": ["B", "B"],
        ...         "result": ["H", "D"],
        ...     }
        ... )
        >>> predictions = walk_forward_predictions(results, FrequencyBaseline(alpha=0), 2021)
        >>> predictions[["p_home", "p_draw", "p_away"]].round(2).values.tolist()
        [[1.0, 0.0, 0.0]]
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
    """Select the matches a team played, home or away.

    Useful for looking at the focus team (Vasco) inside a table of all matches.

    Args:
        matches: A DataFrame with the columns ``home_team`` and ``away_team``.
        team: Club name, spelled exactly as in the data (for example ``"Vasco"``).

    Returns:
        The rows where ``team`` played at home or away, with the same columns and
        the original index.

    Examples:
        >>> import pandas as pd
        >>> frame = pd.DataFrame(
        ...     {"home_team": ["Vasco", "Gremio"], "away_team": ["Gremio", "Santos"]}
        ... )
        >>> matches_of(frame, "Vasco").index.tolist()
        [0]
    """
    return matches[(matches["home_team"] == team) | (matches["away_team"] == team)]
