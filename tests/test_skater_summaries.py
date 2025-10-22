import os
import polars as pl

from pyhockey.skater_summary import skater_summary


TEST_RESULT_PATH = os.path.join('tests', 'expected_results')


def test_standard_skater_summary():
    """
    Test that a standard request from skater_summaries gives a DF of the proper shape.    
    """
    expected: pl.DataFrame = pl.read_csv(os.path.join(TEST_RESULT_PATH, 'skater_summary.csv'))
    result: pl.DataFrame = skater_summary(season=[2023, 2024], team=['TOR', 'MTL'],
                                            min_icetime=500)

    assert result.shape == expected.shape


def test_combined_skater_summary():
    """
    Test that a request using combined_seasons = True gives a DF of the proper shape.
    """
    expected: pl.DataFrame = pl.read_csv(os.path.join(TEST_RESULT_PATH,
                                                      'skater_summaries_combined_seasons.csv'))
    result: pl.DataFrame = skater_summary(season=[2023, 2024], team=['TOR', 'MTL'],
                                            min_icetime=500,
                                            combine_seasons=True)

    assert result.shape == expected.shape
