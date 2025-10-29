import polars as pl

from pyhockey.goalie_games import goalie_games


def test_standard_goalie_games():
    """
    Test that a standard request from goalie_games gives a DF of the expected shape.
    """

    result: pl.DataFrame = goalie_games(name=['Stolarz', 'Shesterkin'], start_date='2025-10-01',
                                        end_date='2025-10-25')

    assert result.shape == (14, 10)
