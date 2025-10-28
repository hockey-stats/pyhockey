import polars as pl

from pyhockey.skater_games import skater_games


def test_standard_skater_games():
    """
    Test that a standard request from skater_games gives a DF of the expected shape.
    """

    result: pl.DataFrame = skater_games(name=['Nylander', 'Matthews'], start_date='2025-10-01',
                                        end_date='2025-10-25')
    
    assert result.shape == (17, 22)
