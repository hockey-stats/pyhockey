"""
Main module for returning season summaries for teams.
"""

import polars as pl

from .util.query_table import query_table


# Define custom type for inputs into our queries
type QueryValue = str | int | float | list[str] | list[int] | list[float]



def team_summary(season: int | list[int],
                 team: str | list[str] = 'ALL',
                 situation: str = 'all',
                 combine_seasons: bool = False) -> pl.DataFrame:
    """
    Primary function for retrieving team-level season summaries. Given a season or list of
    seasons, return team data summaries for each of those seasons

    Can provide further filters via a team or list of teams or a specific situation/game state.

    :param int | list[int] season: The (list of) season(s) for which to return data
    :param str | list[str] team: The (list of) team(s) for which to return data, defaults to 'ALL'
    :param int min_icetime: A minimum icetime (in minutes) cut-off to apply, defaults to 0
    :param str situation: One of 'all', '5on5', '4on5', '5on4', or 'other', defaults to 'all'
    :param bool combine_seasons: If True, and given multiple seasons, combine the results of each
                                 season into a single entry for each player, defaults to False

    :return pl.DataFrame: The resulting data in a polars DataFrame
    """

    column_mapping: dict[str] = {
        'season': season,
        'team': team,
        'situation': situation
    }

    # If getting results for all team, no need to provide a team filter in the column mapping
    if team == 'ALL':
        del column_mapping['team']

    results: pl.DataFrame = query_table(table='teams', column_mapping=column_mapping,
                                        combine_seasons=combine_seasons,
                                        order_by=['team', 'season'])

    return results
