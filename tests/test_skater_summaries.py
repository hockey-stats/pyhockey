import polars as pl

from pyhockey.skater_summary import skater_summary


def test_standard_skater_summary():
    """
    Test that a standard request from skater_summaries gives a DF of the proper shape.    
    """
    result: pl.DataFrame = skater_summary(season=[2023, 2024], team=['TOR', 'MTL'],
                                            min_icetime=500)

    assert result.shape == (79, 31)


def test_combined_skater_summary():
    """
    Test that a request using combined_seasons = True gives a DF of the proper shape.
    """
    result: pl.DataFrame = skater_summary(season=[2023, 2024], team=['TOR', 'MTL'],
                                            min_icetime=500,
                                            combine_seasons=True)

    assert result.shape == (53, 31)
