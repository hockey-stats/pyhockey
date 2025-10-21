import os
import polars as pl

from pyhockey.goalie_summary import goalie_summaries


TEST_RESULT_PATH = os.path.join('tests', 'expected_results')


def test_standard_goalie_summary():
    """
    Test that a standard request from goalie_summaries gives a DF of the proper shape.    
    """
    expected: pl.DataFrame = pl.read_csv(os.path.join(TEST_RESULT_PATH, 'goalie_summary.csv'))
    result: pl.DataFrame = goalie_summaries(season=[2023, 2024], team=['TOR', 'MTL'],
                                            min_games_played=10)

    assert result.shape == expected.shape

    secrets: inherit

def test_combined_goalie_summary():
    """
    Test that a request using combined_seasons = True gives a DF of the proper shape.
    """
    expected: pl.DataFrame = pl.read_csv(os.path.join(TEST_RESULT_PATH,
                                                      'goalie_summaries_combined_seasons.csv'))
    result: pl.DataFrame = goalie_summaries(season=[2023, 2024], team=['TOR', 'MTL'],
                                            min_games_played=10,
                                            combine_seasons=True)

    assert result.shape == expected.shape
