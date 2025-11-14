import polars as pl

from pyhockey.team_seasons import team_seasons


def test_standard_team_seasons():
    """
    Test that a standard request from team_seasons gives a DF of the proper shape.    
    """
    result: pl.DataFrame = team_seasons(season=2023)

    assert result.shape == (32, 13)


def test_combined_team_seasons():
    """
    Test that a request using combined_seasons = True gives a DF of the proper shape.
    """
    result: pl.DataFrame = team_seasons(season=[2023, 2024], combine_seasons=True)

    assert result.shape == (33, 14)
