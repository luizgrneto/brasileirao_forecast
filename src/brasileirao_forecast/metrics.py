"""Scoring rules for win/draw/loss probability forecasts.

Every function here compares forecast probabilities with what actually happened.
Probabilities are always ordered like ``RESULT_LABELS``: home win, draw, away win.
Lower is better for every metric.

The primary metric of the project is the Ranked Probability Score (``rps``);
``log_loss`` and ``brier_score`` are secondary. ``score_predictions`` and
``score_by_season`` apply all three to a table of predictions.

Attributes:
    PROB_COLUMNS: Names of the probability columns in a predictions table, in
        the order home win, draw, away win.
"""

from collections.abc import Sequence

import numpy as np
import pandas as pd

from brasileirao_forecast.loaders import RESULT_LABELS

PROB_COLUMNS = ["p_home", "p_draw", "p_away"]
_INDEX = {label: i for i, label in enumerate(RESULT_LABELS)}
_EPSILON = 1e-15  # keeps log-loss finite when a model gives probability 0 to what happened


def outcome_indices(outcomes: Sequence[str]) -> np.ndarray:
    """Map result labels to their column positions in a probability array.

    Args:
        outcomes: Result labels, each one of ``RESULT_LABELS`` (``"H"``, ``"D"``
            or ``"A"``).

    Returns:
        An integer array with the same length as ``outcomes``: 0 for ``"H"``,
        1 for ``"D"`` and 2 for ``"A"``.

    Raises:
        ValueError: If any label is not in ``RESULT_LABELS``.

    Examples:
        >>> outcome_indices(["H", "A", "D"]).tolist()
        [0, 2, 1]
    """
    try:
        return np.array([_INDEX[label] for label in outcomes], dtype=int)
    except KeyError as error:
        raise ValueError(
            f"unknown result label {error}; expected one of {RESULT_LABELS}"
        ) from error


def _validate(probs, outcomes) -> tuple[np.ndarray, np.ndarray]:
    """Check forecasts and outcomes and put them in the shape the metrics expect.

    Args:
        probs: Array-like of shape ``(n_matches, 3)`` with the forecast
            probabilities of home win, draw and away win.
        outcomes: Result labels, one per match, aligned with the rows of ``probs``.

    Returns:
        A tuple ``(probs, indices)``: the probabilities as a float array and the
        observed outcomes as column positions (see ``outcome_indices``).

    Raises:
        ValueError: If ``probs`` does not have three columns, is empty, differs in
            length from ``outcomes``, has negative values or rows that do not sum
            to 1, or if ``outcomes`` has an unknown label.
    """
    probs = np.asarray(probs, dtype=float)
    if probs.ndim != 2 or probs.shape[1] != len(RESULT_LABELS):
        raise ValueError(f"probs must have shape (n_matches, {len(RESULT_LABELS)})")
    if len(probs) == 0:
        raise ValueError("no matches to score")
    if len(probs) != len(outcomes):
        raise ValueError("probs and outcomes must have the same length")
    if (probs < 0).any() or not np.allclose(probs.sum(axis=1), 1.0, atol=1e-6):
        raise ValueError("probabilities must be non-negative and sum to 1 for each match")
    return probs, outcome_indices(outcomes)


def rps(probs, outcomes) -> float:
    """Compute the Ranked Probability Score, averaged over matches.

    The RPS treats win/draw/loss as ordered (home win < draw < away win), so
    predicting a home win when the away team won costs more than predicting a
    draw. For one match with ``r = 3`` outcomes it is::

        RPS = 1 / (r - 1) * sum over k = 1..r-1 of (sum over j <= k of (p_j - o_j)) ** 2

    where ``p_j`` is the forecast probability of outcome ``j`` and ``o_j`` is 1 if
    that outcome happened and 0 otherwise. Equivalently: the squared errors of the
    two cumulative questions "does the home team win?" and "does the home team win
    or draw?", averaged. The result is the mean over all matches.

    Args:
        probs: Array-like of shape ``(n_matches, 3)`` with the forecast
            probabilities of home win, draw and away win. Each row must be
            non-negative and sum to 1.
        outcomes: Result labels (``"H"``, ``"D"`` or ``"A"``), one per match,
            aligned with the rows of ``probs``.

    Returns:
        The mean RPS, from 0 (perfect) to 1 (certain and completely wrong). Lower
        is better.

    Raises:
        ValueError: If the inputs are invalid (see ``_validate``).

    Examples:
        >>> round(rps([[0.5, 0.3, 0.2]], ["H"]), 3)
        0.145
        >>> round(rps([[0.5, 0.3, 0.2]], ["A"]), 3)
        0.445
    """
    probs, idx = _validate(probs, outcomes)
    observed = np.eye(len(RESULT_LABELS))[idx]
    cumulative_gap = np.cumsum(probs - observed, axis=1)[:, :-1]
    return float(np.mean(np.sum(cumulative_gap**2, axis=1) / (len(RESULT_LABELS) - 1)))


def log_loss(probs, outcomes) -> float:
    """Compute the log-loss, averaged over matches.

    For each match, take minus the natural log of the probability the model gave
    to what actually happened. Unlike ``rps``, it ignores the order of the
    outcomes: only the probability of the observed one matters. Probabilities are
    clipped at ``1e-15`` so a forecast of exactly 0 for the real outcome yields a
    large but finite loss.

    Args:
        probs: Array-like of shape ``(n_matches, 3)`` with the forecast
            probabilities of home win, draw and away win. Each row must be
            non-negative and sum to 1.
        outcomes: Result labels (``"H"``, ``"D"`` or ``"A"``), one per match,
            aligned with the rows of ``probs``.

    Returns:
        The mean log-loss, from 0 (perfect) upwards. Lower is better.

    Raises:
        ValueError: If the inputs are invalid (see ``_validate``).

    Examples:
        >>> round(log_loss([[0.5, 0.3, 0.2]], ["H"]), 4)
        0.6931
    """
    probs, idx = _validate(probs, outcomes)
    chosen = probs[np.arange(len(probs)), idx]
    return float(-np.mean(np.log(np.clip(chosen, _EPSILON, 1.0))))


def brier_score(probs, outcomes) -> float:
    """Compute the multiclass Brier score, averaged over matches.

    For each match, sum the squared difference between the forecast probability
    and what happened (1 for the real outcome, 0 for the others) over the three
    outcomes. Like ``log_loss``, it ignores the order of the outcomes.

    Args:
        probs: Array-like of shape ``(n_matches, 3)`` with the forecast
            probabilities of home win, draw and away win. Each row must be
            non-negative and sum to 1.
        outcomes: Result labels (``"H"``, ``"D"`` or ``"A"``), one per match,
            aligned with the rows of ``probs``.

    Returns:
        The mean Brier score, from 0 (perfect) to 2 (certain and completely
        wrong). Lower is better.

    Raises:
        ValueError: If the inputs are invalid (see ``_validate``).

    Examples:
        >>> round(brier_score([[0.5, 0.3, 0.2]], ["H"]), 2)
        0.38
    """
    probs, idx = _validate(probs, outcomes)
    observed = np.eye(len(RESULT_LABELS))[idx]
    return float(np.mean(np.sum((probs - observed) ** 2, axis=1)))


def score_predictions(predictions: pd.DataFrame) -> dict[str, float]:
    """Score a table of predictions with every metric of the project.

    Args:
        predictions: A DataFrame with one row per match, the probability columns
            in ``PROB_COLUMNS`` and a ``result`` column with the labels
            ``"H"``, ``"D"`` or ``"A"``. Other columns are ignored.

    Returns:
        A dictionary with the number of matches (``"n"``) and the mean ``"rps"``,
        ``"log_loss"`` and ``"brier"``.

    Raises:
        KeyError: If the probability columns or ``result`` are missing.
        ValueError: If the probabilities or labels are invalid, or if
            ``predictions`` is empty.

    Examples:
        >>> import pandas as pd
        >>> frame = pd.DataFrame(
        ...     {"p_home": [0.5], "p_draw": [0.3], "p_away": [0.2], "result": ["H"]}
        ... )
        >>> scores = score_predictions(frame)
        >>> scores["n"], round(scores["rps"], 3)
        (1, 0.145)
    """
    probs = predictions[PROB_COLUMNS].to_numpy()
    outcomes = predictions["result"].to_numpy()
    return {
        "n": len(predictions),
        "rps": rps(probs, outcomes),
        "log_loss": log_loss(probs, outcomes),
        "brier": brier_score(probs, outcomes),
    }


def score_by_season(predictions: pd.DataFrame) -> pd.DataFrame:
    """Score a table of predictions separately for each season.

    Args:
        predictions: A DataFrame as described in ``score_predictions``, plus a
            ``season`` column used to group the matches.

    Returns:
        A DataFrame indexed by season (index named ``season``), with one row per
        season and the columns ``n`` (int), ``rps``, ``log_loss`` and ``brier``.

    Raises:
        KeyError: If ``season``, the probability columns or ``result`` are missing.
        ValueError: If the probabilities or labels are invalid.

    Examples:
        >>> import pandas as pd
        >>> frame = pd.DataFrame(
        ...     {
        ...         "season": [2020, 2021],
        ...         "p_home": [0.5, 0.5],
        ...         "p_draw": [0.3, 0.3],
        ...         "p_away": [0.2, 0.2],
        ...         "result": ["H", "A"],
        ...     }
        ... )
        >>> score_by_season(frame)["rps"].round(3).tolist()
        [0.145, 0.445]
    """
    rows = {season: score_predictions(group) for season, group in predictions.groupby("season")}
    scores = pd.DataFrame.from_dict(rows, orient="index")
    scores.index.name = "season"
    return scores.astype({"n": int})
