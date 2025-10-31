"""
Main module for returning game-by-game statistics for each team.
"""
import polars as pl

from pyhockey.util.query_table import query_table
from pyhockey.util.data_disclaimer import print_data_disclaimer


# Define custom type for inputs into our queries
type QueryValue = str | int | float | list[str] | list[int] | list[float]


def team_games(season: int | list[int] | None = None,
               team: str | list[str] = 'ALL',
               start_date: str | None = None,
               end_date: str | None = None,
               situation: str = 'all',
               quiet: bool = False) -> pl.DataFrame:
    """ Return team-level game-by-game statistics

    Primary function for returning game-by-game team statistics. Accepts one or multiple teams, one
    or multiple seasons, or alternatively, a start- and end-date for which to return game-by-game
    metrics.

    Args:

        season: 
            Either one or a list of seasons for which to return all games. Disregarded if both
            start_date and end_date are also provided, defaults to None
        team: 
            Either one or a list of teams, provided in 3-letter acronyms, defaults to 'ALL'
        start_date: 
            A date from which to return all games on and after that date, in YYYY-MM-DD format,
            defaults to None
        end_date: 
            A date from which to return all games before and on that date, in YYYY-MM-DD format,
            defaults to None
        situation: 
            One of 'all', '5on5', '4on5', or '5on4', defaults to 'all'
        quiet: 
            If set to True, don't print the data disclaimer, defaults to False
    
    Returns:

        A polars DataFrame containing all of the requested data.

    Raises:
    
        ValueError: An input of either incorrect value or type was provided.
    """

    if not season and not start_date and not end_date:
        raise ValueError("No values provided for 'season', 'start_date', or 'end_date'. Must "\
                         "provide value for at least one of these.")

    qualifers: dict[str, str] = {}

    if start_date:
        qualifers['start_date'] = start_date
    if end_date:
        qualifers['end_date'] = end_date

    column_mapping: dict[str, QueryValue] = {
        'season': season,
        'team': team,
        'situation': situation
    }

    results: pl.DataFrame = query_table(table='team_games', column_mapping=column_mapping,
                                        qualifiers=qualifers, order_by=['team', 'gameDate'])

    if not quiet:
        print_data_disclaimer(source='MoneyPuck')

    return results
