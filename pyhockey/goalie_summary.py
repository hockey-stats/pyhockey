"""
Module for handling calls to the 'goalies' table, which holds season summaries for each goalie,
divided by game state.
"""

import polars as pl

from pyhockey.util.query_table import query_table


# Define custom type for inputs into our queries
type QueryValue = str | int | float | list[str] | list[int] | list[float]


def goalie_summary(season: int | list[int],
                   team: str | list[str] = 'ALL',
                   min_games_played: int = 0,
                   situation: str = 'all',
                   combine_seasons: bool = False) -> pl.DataFrame:
    """
    Primary function for retrieving goalie-level season summaries. Given a season or list of
    seasons, return goalie data summaries for each of those seasons. 

    Can provide further filters via a team or list of teams, a minimum icetime cutoff, or
    a specific situation/game state.

    :param int | list[int] season: The (list of) season(s) for which to return data
    :param str | list[str] team: The (list of) team(s) for which to return data, defaults to 'ALL'
    :param int min_icetime: A minimum icetime (in minutes) cut-off to apply, defaults to 0
    :param str situation: One of 'all', '5on5', '4on5', '5on4', or 'other', defaults to 'all'
    :param bool combine_seasons: If True, and given multiple seasons, combine the results of each
                                 season into a single entry for each player, defaults to False

    :return pl.DataFrame: The resulting data in a polars DataFrame
    """

    column_mapping: dict[str, QueryValue] = {
        'season': season,
        'team': team,
        'situation': situation
    }

    qualifiers: dict[str, str] = {
        'gamesPlayed': f'>={min_games_played}'
    }

    results: pl.DataFrame = query_table(table='goalies', column_mapping=column_mapping,
                                        qualifiers=qualifiers, combine_seasons=combine_seasons,
                                        order_by=['team', 'season'])

    return results
