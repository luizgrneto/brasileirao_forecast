"""The naive reference every model has to beat."""

import numpy as np
import pandas as pd

from brasileirao_forecast.loaders import RESULT_LABELS


class FrequencyBaseline:
    """Predicts the same probabilities for every match: how often each result happened.

    The probabilities are the historical shares of home wins, draws and away wins,
    with optional add-``alpha`` smoothing so that no outcome ever gets exactly 0.
    It knows nothing about the teams playing, which is the point: it is the
    yardstick that shows what knowing the teams has to add.
    """

    def __init__(self, alpha: float = 1.0):
        if alpha < 0:
            raise ValueError("alpha must be non-negative")
        self.alpha = alpha
        self._probs: np.ndarray | None = None

    def fit(self, history: pd.DataFrame) -> "FrequencyBaseline":
        """Learn the result frequencies from played matches (needs a ``result`` column)."""
        if history.empty:
            raise ValueError("cannot fit on an empty history")
        counts = (
            history["result"].value_counts().reindex(RESULT_LABELS, fill_value=0).to_numpy(float)
        )
        self._probs = (counts + self.alpha) / (counts.sum() + self.alpha * len(RESULT_LABELS))
        return self

    def predict(self, matches: pd.DataFrame) -> np.ndarray:
        """Return an ``(n_matches, 3)`` array of home/draw/away probabilities."""
        if self._probs is None:
            raise RuntimeError("call fit before predict")
        return np.tile(self._probs, (len(matches), 1))
