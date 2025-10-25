import polars as pl

from pyhockey.team_summary import team_summary


def test_standard_team_summary():
    """
    Test that a standard request from team_summary gives a DF of the proper shape.    
    """
    result: pl.DataFrame = team_summary(season=2023)

    assert result.shape == (32, 13)


def test_combined_team_summary():
    """
    Test that a request using combined_seasons = True gives a DF of the proper shape.
    """
    result: pl.DataFrame = team_summary(season=[2023, 2024], combine_seasons=True)

    assert result.shape == (33, 14)
