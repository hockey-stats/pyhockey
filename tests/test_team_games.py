import polars as pl

from pyhockey.team_games import team_games


def test_standard_team_games():
    """
    Test that a standard request from team_games gives a DF of the expected shape.
    """
    result: pl.DataFrame = team_games(team='TOR', start_date='2024-10-01',
                                      end_date='2025-01-23')

    assert result.shape == (245, 15)
