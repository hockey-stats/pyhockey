"""
Main module for returning game-by-game statistics for each team.
"""
import polars as pl

from pyhockey.util.query_table import query_table


# Define custom type for inputs into our queries
type QueryValue = str | int | float | list[str] | list[int] | list[float]


def team_games(season: int | list[int] | None = None,
               team: str | list[str] = 'ALL',
               start_date: str | None = None,
               end_date: str | None = None,
               situation: str = 'all') -> pl.DataFrame:
    """
    Primary function for returning game-by-game team statistics. Accepts one or multiple teams, one
    or multiple seasons, or alternatively, a start- and end-date for which to return game-by-game
    metrics.

    :param int | list[int] | None season: Either one or a list of seasons for which to return all
                                          games. Disregarded if both start_date and end_date are
                                          also provided, defaults to None
    :param str | list[str] team: Either one or a list of teams, provided in 3-letter acronyms, 
                                 defaults to 'ALL'
    :param str | None start_date: A date from which to return all games on and after that date, in
                                  YYYY-MM-DD format, defaults to None
    :param str | None end_date: A date from which to return all games before and on that date, in
                                YYYY-MM-DD format, defaults to None
    :param str situation: One of 'all', '5on5', '4on5', or '5on4', defaults to 'all'
    
    :raises ValueError: Raises a ValueError if incorrect date format is provided.
    
    :return pl.DataFrame: A DataFrame containing the requested data.
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

    # Remove inputs from the column_mapping if they're not used
    for key, value in zip(['season', 'team'], [season, team]):
        if value is None or (key == 'team' and value == 'ALL'):
            del column_mapping[key]

    results: pl.DataFrame = query_table(table='team_games', column_mapping=column_mapping,
                                        qualifiers=qualifers, order_by=['team', 'gameDate'])

    return results
