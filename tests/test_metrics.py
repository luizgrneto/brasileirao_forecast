import numpy as np
import pandas as pd
import pytest

from brasileirao_forecast.metrics import (
    PROB_COLUMNS,
    brier_score,
    log_loss,
    outcome_indices,
    rps,
    score_by_season,
    score_predictions,
)

FORECAST = [[0.5, 0.3, 0.2]]


@pytest.mark.parametrize(
    ("outcome", "expected"),
    [
        # cumulative gaps for a home win: (0.5-1, 0.8-1) -> (0.25 + 0.04) / 2
        ("H", 0.145),
        # draw: (0.5-0, 0.8-1) -> (0.25 + 0.04) / 2
        ("D", 0.145),
        # away win: (0.5-0, 0.8-0) -> (0.25 + 0.64) / 2
        ("A", 0.445),
    ],
)
def test_rps_matches_hand_computed_values(outcome, expected):
    assert rps(FORECAST, [outcome]) == pytest.approx(expected)


def test_rps_is_zero_for_a_perfect_forecast():
    assert rps([[1, 0, 0], [0, 0, 1]], ["H", "A"]) == pytest.approx(0.0)


def test_rps_punishes_distant_mistakes_more_than_near_ones():
    certain_home = [[1.0, 0.0, 0.0]]
    assert rps(certain_home, ["A"]) > rps(certain_home, ["D"])


def test_rps_is_one_when_certain_and_completely_wrong():
    assert rps([[1.0, 0.0, 0.0]], ["A"]) == pytest.approx(1.0)


def test_log_loss_is_minus_log_of_the_probability_of_the_outcome():
    assert log_loss(FORECAST, ["H"]) == pytest.approx(-np.log(0.5))


def test_log_loss_stays_finite_when_probability_is_zero():
    assert np.isfinite(log_loss([[1.0, 0.0, 0.0]], ["A"]))


def test_brier_score_matches_hand_computed_value():
    # (0.5-1)^2 + 0.3^2 + 0.2^2
    assert brier_score(FORECAST, ["H"]) == pytest.approx(0.38)


def test_metrics_average_over_matches():
    probs = [[0.5, 0.3, 0.2], [0.5, 0.3, 0.2]]
    assert rps(probs, ["H", "A"]) == pytest.approx((0.145 + 0.445) / 2)


@pytest.mark.parametrize(
    "probs",
    [
        [[0.5, 0.3, 0.3]],  # does not sum to 1
        [[-0.1, 0.6, 0.5]],  # negative probability
        [[0.5, 0.5]],  # wrong number of outcomes
    ],
)
def test_invalid_probabilities_raise(probs):
    with pytest.raises(ValueError):
        rps(probs, ["H"])


def test_unknown_label_raises():
    with pytest.raises(ValueError, match="unknown result label"):
        outcome_indices(["H", "X"])


def test_length_mismatch_raises():
    with pytest.raises(ValueError, match="same length"):
        rps(FORECAST, ["H", "D"])


def test_empty_input_raises():
    with pytest.raises(ValueError, match="no matches"):
        rps(np.empty((0, 3)), [])


def make_predictions():
    return pd.DataFrame(
        {
            "season": [2020, 2020, 2021],
            "result": ["H", "A", "D"],
            "p_home": [0.5, 0.5, 0.5],
            "p_draw": [0.3, 0.3, 0.3],
            "p_away": [0.2, 0.2, 0.2],
        }
    )


def test_score_predictions_returns_all_metrics():
    scores = score_predictions(make_predictions())

    assert scores["n"] == 3
    assert scores["rps"] == pytest.approx((0.145 + 0.445 + 0.145) / 3)
    assert set(scores) == {"n", "rps", "log_loss", "brier"}


def test_score_by_season_has_one_row_per_season():
    scores = score_by_season(make_predictions())

    assert list(scores.index) == [2020, 2021]
    assert list(scores["n"]) == [2, 1]
    assert scores.loc[2021, "rps"] == pytest.approx(0.145)


def test_prob_columns_follow_result_order():
    assert PROB_COLUMNS == ["p_home", "p_draw", "p_away"]
