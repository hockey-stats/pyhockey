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

    if not season:
        del column_mapping['season']

    results: pl.DataFrame = query_table(table='team_games', column_mapping=column_mapping,
                                        qualifiers=qualifers, order_by=['team', 'gameDate'])

    return results


if __name__ == '__main__':
    print(team_games(team='TOR', start_date='10-10-2024', end_date='2025-10-23'))
