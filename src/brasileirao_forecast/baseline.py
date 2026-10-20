"""The naive reference every model has to beat.

The baseline ignores which teams are playing and always forecasts how often each
result has happened. Its score is the yardstick that shows what knowing the teams
has to add.
"""

import numpy as np
import pandas as pd

from brasileirao_forecast.loaders import RESULT_LABELS


class FrequencyBaseline:
    """Predicts the same probabilities for every match: how often each result happened.

    The probabilities are the historical shares of home wins, draws and away wins,
    with optional add-``alpha`` smoothing so that no outcome ever gets exactly 0.
    It knows nothing about the teams playing, which is the point: it is the
    yardstick that shows what knowing the teams has to add.

    The class follows the ``Model`` protocol of ``brasileirao_forecast.evaluation``
    (``fit`` on played matches, ``predict`` for upcoming ones), so it can be
    evaluated like any other model.

    Attributes:
        alpha: Smoothing pseudo-count added to each outcome before normalising.

    Examples:
        >>> import pandas as pd
        >>> history = pd.DataFrame({"result": ["H", "H", "D", "A"]})
        >>> model = FrequencyBaseline(alpha=0).fit(history)
        >>> model.predict(pd.DataFrame(index=range(2))).round(2).tolist()
        [[0.5, 0.25, 0.25], [0.5, 0.25, 0.25]]
    """

    def __init__(self, alpha: float = 1.0):
        """Create an unfitted baseline.

        Args:
            alpha: Smoothing pseudo-count added to the count of each result
                before turning counts into probabilities. With ``0`` the
                probabilities are the raw frequencies; with ``1`` (the default)
                no result can get probability exactly 0.

        Raises:
            ValueError: If ``alpha`` is negative.
        """
        if alpha < 0:
            raise ValueError("alpha must be non-negative")
        self.alpha = alpha
        self._probs: np.ndarray | None = None

    def fit(self, history: pd.DataFrame) -> "FrequencyBaseline":
        """Learn the result frequencies from played matches.

        Args:
            history: Played matches, with a ``result`` column of labels from
                ``RESULT_LABELS``. Rows with any other label are ignored when
                counting.

        Returns:
            The fitted baseline itself, so calls can be chained.

        Raises:
            ValueError: If ``history`` is empty.
        """
        if history.empty:
            raise ValueError("cannot fit on an empty history")
        counts = (
            history["result"].value_counts().reindex(RESULT_LABELS, fill_value=0).to_numpy(float)
        )
        self._probs = (counts + self.alpha) / (counts.sum() + self.alpha * len(RESULT_LABELS))
        return self

    def predict(self, matches: pd.DataFrame) -> np.ndarray:
        """Forecast the given matches with the learned frequencies.

        Args:
            matches: The matches to forecast. Only the number of rows matters,
                since every match gets the same probabilities.

        Returns:
            An array of shape ``(n_matches, 3)`` whose every row holds the
            probabilities of home win, draw and away win, in that order.

        Raises:
            RuntimeError: If called before ``fit``.
        """
        if self._probs is None:
            raise RuntimeError("call fit before predict")
        return np.tile(self._probs, (len(matches), 1))
