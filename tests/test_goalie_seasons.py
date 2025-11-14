import polars as pl

from pyhockey.goalie_seasons import goalie_seasons


def test_standard_goalie_seasons():
    """
    Test that a standard request from goalie_seasons gives a DF of the proper shape.    
    """
    result: pl.DataFrame = goalie_seasons(season=[2023, 2024], team=['TOR', 'MTL'],
                                            min_games_played=10)

    assert result.shape == (10, 18)


def test_combined_goalie_seasons():
    """
    Test that a request using combined_seasons = True gives a DF of the proper shape.
    """
    result: pl.DataFrame = goalie_seasons(season=[2023, 2024], team=['TOR', 'MTL'],
                                          min_games_played=10,
                                          combine_seasons=True)

    assert result.shape == (7, 18)
