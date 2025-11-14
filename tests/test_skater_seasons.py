import polars as pl

from pyhockey.skater_seasons import skater_seasons


def test_standard_skater_seasons():
    """
    Test that a standard request from skater_seasons gives a DF of the proper shape.    
    """
    result: pl.DataFrame = skater_seasons(season=[2023, 2024], team=['TOR', 'MTL'],
                                            min_icetime=500)

    assert result.shape == (79, 31)


def test_combined_skater_seasons():
    """
    Test that a request using combined_seasons = True gives a DF of the proper shape.
    """
    result: pl.DataFrame = skater_seasons(season=[2023, 2024], team=['TOR', 'MTL'],
                                            min_icetime=500,
                                            combine_seasons=True)

    assert result.shape == (53, 31)
