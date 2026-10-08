"""Scoring rules for win/draw/loss probability forecasts.

Probabilities are always ordered like ``RESULT_LABELS``: home win, draw, away win.
Lower is better for every metric here.
"""

from collections.abc import Sequence

import numpy as np
import pandas as pd

from brasileirao_forecast.loaders import RESULT_LABELS

PROB_COLUMNS = ["p_home", "p_draw", "p_away"]
_INDEX = {label: i for i, label in enumerate(RESULT_LABELS)}
_EPSILON = 1e-15  # keeps log-loss finite when a model gives probability 0 to what happened


def outcome_indices(outcomes: Sequence[str]) -> np.ndarray:
    """Map result labels ("H", "D", "A") to column positions 0, 1, 2."""
    try:
        return np.array([_INDEX[label] for label in outcomes], dtype=int)
    except KeyError as error:
        raise ValueError(
            f"unknown result label {error}; expected one of {RESULT_LABELS}"
        ) from error


def _validate(probs, outcomes) -> tuple[np.ndarray, np.ndarray]:
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
    """Ranked Probability Score, averaged over matches.

    Treats win/draw/loss as ordered (home win < draw < away win), so predicting a
    home win when the away team won costs more than predicting a draw. Ranges from
    0 (perfect) to 1 (certain and completely wrong).
    """
    probs, idx = _validate(probs, outcomes)
    observed = np.eye(len(RESULT_LABELS))[idx]
    cumulative_gap = np.cumsum(probs - observed, axis=1)[:, :-1]
    return float(np.mean(np.sum(cumulative_gap**2, axis=1) / (len(RESULT_LABELS) - 1)))


def log_loss(probs, outcomes) -> float:
    """Average negative log of the probability given to what actually happened."""
    probs, idx = _validate(probs, outcomes)
    chosen = probs[np.arange(len(probs)), idx]
    return float(-np.mean(np.log(np.clip(chosen, _EPSILON, 1.0))))


def brier_score(probs, outcomes) -> float:
    """Multiclass Brier score: squared error summed over the three outcomes, averaged."""
    probs, idx = _validate(probs, outcomes)
    observed = np.eye(len(RESULT_LABELS))[idx]
    return float(np.mean(np.sum((probs - observed) ** 2, axis=1)))


def score_predictions(predictions: pd.DataFrame) -> dict[str, float]:
    """Score a frame with ``PROB_COLUMNS`` and ``result`` columns."""
    probs = predictions[PROB_COLUMNS].to_numpy()
    outcomes = predictions["result"].to_numpy()
    return {
        "n": len(predictions),
        "rps": rps(probs, outcomes),
        "log_loss": log_loss(probs, outcomes),
        "brier": brier_score(probs, outcomes),
    }


def score_by_season(predictions: pd.DataFrame) -> pd.DataFrame:
    """One row of scores per season."""
    rows = {season: score_predictions(group) for season, group in predictions.groupby("season")}
    scores = pd.DataFrame.from_dict(rows, orient="index")
    scores.index.name = "season"
    return scores.astype({"n": int})
