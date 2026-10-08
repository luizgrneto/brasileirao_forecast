import numpy as np
import pandas as pd
import pytest

from brasileirao_forecast.baseline import FrequencyBaseline


def history(results):
    return pd.DataFrame({"result": results})


def test_learns_result_frequencies_without_smoothing():
    model = FrequencyBaseline(alpha=0).fit(history(["H", "H", "D", "A"]))

    probs = model.predict(pd.DataFrame(index=range(2)))

    assert probs.shape == (2, 3)
    np.testing.assert_allclose(probs[0], [0.5, 0.25, 0.25])
    np.testing.assert_allclose(probs[0], probs[1])


def test_smoothing_keeps_every_outcome_possible():
    model = FrequencyBaseline(alpha=1.0).fit(history(["H", "H", "H"]))

    probs = model.predict(pd.DataFrame(index=range(1)))[0]

    assert (probs > 0).all()
    assert probs.sum() == pytest.approx(1.0)
    assert probs[0] > probs[1]


def test_predict_before_fit_raises():
    with pytest.raises(RuntimeError, match="fit"):
        FrequencyBaseline().predict(pd.DataFrame(index=range(1)))


def test_fit_on_empty_history_raises():
    with pytest.raises(ValueError, match="empty"):
        FrequencyBaseline().fit(history([]))


def test_negative_alpha_raises():
    with pytest.raises(ValueError, match="alpha"):
        FrequencyBaseline(alpha=-1)
