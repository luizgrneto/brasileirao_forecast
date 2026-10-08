import numpy as np
import pandas as pd
import pytest

from brasileirao_forecast.baseline import FrequencyBaseline
from brasileirao_forecast.evaluation import matches_of, walk_forward_predictions
from brasileirao_forecast.metrics import PROB_COLUMNS


def make_results(rows):
    """rows: (season, date, home, away, result) -> frame shaped like load_results."""
    return pd.DataFrame(
        {
            "season": [r[0] for r in rows],
            "kickoff": pd.to_datetime([f"{r[1]} 20:00" for r in rows]),
            "home_team": [r[2] for r in rows],
            "away_team": [r[3] for r in rows],
            "result": [r[4] for r in rows],
        }
    )


ROWS = [
    (2020, "2020-01-01", "A", "B", "H"),
    (2020, "2020-01-02", "C", "D", "H"),
    (2020, "2020-01-03", "A", "C", "D"),
    (2021, "2021-01-01", "B", "D", "A"),
    (2021, "2021-01-01", "A", "D", "H"),  # same day as the match above
    (2021, "2021-01-02", "B", "C", "D"),
]


class SpyModel:
    """Records how much history each fit saw, and predicts uniform probabilities."""

    def __init__(self):
        self.history_sizes = []

    def fit(self, history):
        self.history_sizes.append(len(history))
        return self

    def predict(self, matches):
        return np.full((len(matches), 3), 1 / 3)


def test_only_test_seasons_are_predicted():
    predictions = walk_forward_predictions(make_results(ROWS), SpyModel(), first_test_season=2021)

    assert set(predictions["season"]) == {2021}
    assert len(predictions) == 3
    assert all(column in predictions.columns for column in PROB_COLUMNS)


def test_each_day_is_fit_only_on_earlier_days():
    spy = SpyModel()

    walk_forward_predictions(make_results(ROWS), spy, first_test_season=2021)

    # 2021-01-01 sees the 3 matches of 2020; 2021-01-02 also sees the 2 played on 2021-01-01
    assert spy.history_sizes == [3, 5]


def test_future_results_do_not_change_earlier_predictions():
    results = make_results(ROWS)
    altered = results.copy()
    altered.loc[altered["kickoff"] >= "2021-01-02", "result"] = "A"

    original = walk_forward_predictions(results, FrequencyBaseline(), 2021)
    changed = walk_forward_predictions(altered, FrequencyBaseline(), 2021)

    first_day = original["kickoff"].dt.normalize() == pd.Timestamp("2021-01-01")
    np.testing.assert_allclose(
        original.loc[first_day, PROB_COLUMNS].to_numpy(),
        changed.loc[first_day, PROB_COLUMNS].to_numpy(),
    )


def test_baseline_predictions_use_all_earlier_matches():
    predictions = walk_forward_predictions(make_results(ROWS), FrequencyBaseline(alpha=0), 2021)

    # 2020 had 2 home wins and 1 draw
    first_day = predictions.iloc[0]
    assert first_day["p_home"] == pytest.approx(2 / 3)
    assert first_day["p_draw"] == pytest.approx(1 / 3)
    assert first_day["p_away"] == pytest.approx(0.0)


def test_raises_without_history_before_first_test_season():
    with pytest.raises(ValueError, match="no history"):
        walk_forward_predictions(make_results(ROWS), SpyModel(), first_test_season=2020)


def test_raises_when_no_matches_in_test_seasons():
    with pytest.raises(ValueError, match="no matches"):
        walk_forward_predictions(make_results(ROWS), SpyModel(), first_test_season=2030)


def test_matches_of_selects_home_and_away_games():
    selected = matches_of(make_results(ROWS), "D")

    assert len(selected) == 3
    assert set(selected["season"]) == {2020, 2021}
