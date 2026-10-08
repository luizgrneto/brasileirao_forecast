import pandas as pd
import pytest

from brasileirao_forecast.loaders import RESULT_LABELS, load_results

HEADER = "Country,League,Season,Date,Time,Home,Away,HG,AG,Res"


def write_csv(tmp_path, rows, header=HEADER):
    """Write a small synthetic CSV (with the BOM the real file has)."""
    path = tmp_path / "BRA.csv"
    path.write_text("\n".join([header, *rows]) + "\n", encoding="utf-8-sig")
    return path


def test_parses_columns_and_types(tmp_path):
    path = write_csv(
        tmp_path,
        [
            "Brazil,Serie A,2020,19/05/2020,22:30,Alpha FC,Beta FC,2.0,1.0,H",
            "Brazil,Serie A,2020,20/05/2020,01:00,Gamma FC,Delta FC,0.0,0.0,D",
        ],
    )

    df = load_results(path)

    assert list(df.columns) == [
        "season",
        "kickoff",
        "home_team",
        "away_team",
        "home_goals",
        "away_goals",
        "result",
    ]
    assert df.loc[0, "kickoff"] == pd.Timestamp("2020-05-19 22:30")
    assert df.loc[0, "home_goals"] == 2
    assert df["home_goals"].dtype.kind == "i"
    assert set(df["result"]) <= set(RESULT_LABELS)


def test_strips_leading_space_in_time(tmp_path):
    path = write_csv(tmp_path, ["Brazil,Serie A,2019,30/10/2019, 22:30,Alpha FC,Beta FC,1.0,0.0,H"])

    df = load_results(path)

    assert df.loc[0, "kickoff"] == pd.Timestamp("2019-10-30 22:30")


def test_drops_matches_without_score(tmp_path):
    path = write_csv(
        tmp_path,
        [
            "Brazil,Serie A,2016,11/12/2016,19:00,Alpha FC,Beta FC,,,",
            "Brazil,Serie A,2016,10/12/2016,19:00,Gamma FC,Delta FC,1.0,2.0,A",
        ],
    )

    df = load_results(path)

    assert len(df) == 1
    assert df.loc[0, "home_team"] == "Gamma FC"


def test_sorts_by_kickoff(tmp_path):
    path = write_csv(
        tmp_path,
        [
            "Brazil,Serie A,2020,21/05/2020,20:00,Alpha FC,Beta FC,1.0,1.0,D",
            "Brazil,Serie A,2020,19/05/2020,20:00,Gamma FC,Delta FC,3.0,0.0,H",
        ],
    )

    df = load_results(path)

    assert df["kickoff"].is_monotonic_increasing


def test_raises_when_result_disagrees_with_score(tmp_path):
    path = write_csv(tmp_path, ["Brazil,Serie A,2020,19/05/2020,22:30,Alpha FC,Beta FC,2.0,1.0,A"])

    with pytest.raises(ValueError, match="disagrees"):
        load_results(path)


def test_raises_on_duplicated_match(tmp_path):
    row = "Brazil,Serie A,2020,19/05/2020,22:30,Alpha FC,Beta FC,2.0,1.0,H"
    path = write_csv(tmp_path, [row, row])

    with pytest.raises(ValueError, match="duplicated"):
        load_results(path)


def test_raises_when_columns_are_missing(tmp_path):
    path = write_csv(tmp_path, ["Brazil,Serie A,2020"], header="Country,League,Season")

    with pytest.raises(ValueError, match="missing required columns"):
        load_results(path)
