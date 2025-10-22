import os
import polars as pl

from pyhockey.team_summary import team_summary


TEST_RESULT_PATH = os.path.join('tests', 'expected_results')


def test_standard_team_summary():
    """
    Test that a standard request from team_summary gives a DF of the proper shape.    
    """
    expected: pl.DataFrame = pl.read_csv(os.path.join(TEST_RESULT_PATH, 'team_summary.csv'))
    result: pl.DataFrame = team_summary(season=2023)

    assert result.shape == expected.shape


def test_combined_team_summary():
    """
    Test that a request using combined_seasons = True gives a DF of the proper shape.
    """
    expected: pl.DataFrame = pl.read_csv(os.path.join(TEST_RESULT_PATH,
                                                      'team_summaries_combined_seasons.csv'))
    result: pl.DataFrame = team_summary(season=[2023, 2024], combine_seasons=True)

    assert result.shape == expected.shape
