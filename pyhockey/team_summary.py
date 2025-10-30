"""
Main module for returning season summaries for teams.
"""

import polars as pl

from pyhockey.util.query_table import query_table
from pyhockey.util.data_disclaimer import print_data_disclaimer


# Define custom type for inputs into our queries
type QueryValue = str | int | float | list[str] | list[int] | list[float]


def team_summary(season: int | list[int],
                 team: str | list[str] = 'ALL',
                 situation: str = 'all',
                 combine_seasons: bool = False,
                 quiet: bool = False) -> pl.DataFrame:
    """ Return team-level season summary data.

    Primary function for retrieving team-level season summaries. Given a season or list of
    seasons, return team data summaries for each of those season.

    Can provide further filters via a team or list of teams or a specific situation/game state.

    Args:
        season: 
            The (list of) season(s) for which to return data
        team: 
            The (list of) team(s) for which to return data, defaults to 'ALL'
        min_icetime: 
            A minimum icetime (in minutes) cut-off to apply, defaults to 0
        situation: 
            One of 'all', '5on5', '4on5', '5on4', or 'other', defaults to 'all'
        combine_seasons: 
            If True, and given multiple seasons, combine the results of each season into a single
            entry for each player, defaults to False
        quiet: 
            If set to True, don't print the data disclaimer, defaults to False

    Returns:
        A polars DataFrame containing all of the requested data.

    Raises:
        ValueError: An input of either incorrect value or type was provided.
    """

    column_mapping: dict[str, QueryValue] = {
        'season': season,
        'team': team,
        'situation': situation
    }

    results: pl.DataFrame = query_table(table='teams', column_mapping=column_mapping,
                                        combine_seasons=combine_seasons,
                                        order_by=['team', 'season'])

    if not quiet:
        print_data_disclaimer(source='MoneyPuck')

    return results
