"""
Module for handling the actual querying of tables in the database. A lot of the logic for querying
is similar between the primary methods, so made sense to just have it abstracted out and handled
seperately, here.
"""
from typing import Callable

import duckdb
import polars as pl
import polars.selectors as sc

from pyhockey.util.db_connect import create_connection
from pyhockey.util.query_builder import construct_query

# Define custom type for inputs into our queries
type QueryValue = str | int | float | list[str] | list[int] | list[float]


def query_table(table: str,
                column_mapping: dict[str, QueryValue],
                qualifiers: dict[str, str] | None = None,
                order_by: list[str] | None = None,
                combine_seasons: bool = False) -> pl.DataFrame:
    """
    Function to handle specifics of querying a table, given the desired table and parameters.

    This function will handle calling the query constructer, retrieving the database connection,
    querying the database, combining season values if desired, and rounding the values in the
    results before returning them.

    :param str table: Name of the table to be querying.
    :param dict[str, QueryValue] column_mapping: A dict mapping column names in the table to values
                                                 they need to be evaluated against. Multiple values
                                                 can be provided in a list and all will be combined
                                                 in an 'OR' statement.
    :param dict[str, str] qualifiers: A dict mapping certain column names to evaluations which will
                                      be applied to the query, e.g. '<' or '>' conditions, defaults 
                                      to None.
    :param list[str] | None order_by: A list of strings corresponding to column names that the 
                                     results will be sorted by, defaults to None.
    :param bool combine_seasons: , defaults to False
    :return pl.DataFrame: _description_
    """

    query: str = construct_query(table_name=table, column_mapping=column_mapping,
                                 qualifiers=qualifiers, order_by=order_by)

    connection: duckdb.DuckDBPyConnection = create_connection()

    results: pl.DataFrame = connection.sql(query).pl()


    if combine_seasons:
        # A dict mapping table names to functions which can be called to combine season rows into
        # single rows
        season_combine_funcs: dict[str, Callable[[pl.DataFrame], pl.DataFrame]] = {
            'teams': combine_team_seasons,
            'skaters': combine_skater_seasons,
            'goalies': combine_goalie_seasons
        }

        if not isinstance(column_mapping['season'], list):
            print(f"The 'combine_seasons' parameter has been set to 'True', but data for only one "\
                  f"season ({column_mapping['season']}) was requested. Returning data for just "\
                  f"that season...")
            return results
        func: Callable[[pl.DataFrame], pl.DataFrame] = season_combine_funcs[table]
        results = func(results)

    # Round all float values to 2 decimal places before returning
    results = results.with_columns(sc.float().round(2))

    # Close the connection after query is complete
    connection.close()

    return results


def combine_team_seasons(df: pl.DataFrame) -> pl.DataFrame:
    """
    Called when a user requests multiple seasons worth of data and wants to have them combined
    into a single row for each team.

    Goes through the data provided by the query and combines the data for each team-season into
    one row, returning the resulting DataFrame.

    :param pl.DataFrame df: The raw results of the query containing rows for each team-season

    :return pl.DataFrame: The output DataFrame with all team-seasons combined into one row.
    """
    # This list will contain DFs for each individual player, to be concatenated at the end
    team_dfs: list[pl.DataFrame] = []

    # For each unique player, create a filtered DF of just their data and use it to create
    # a dict summarizing the info.
    for team in set(df['team']):
        t_df: pl.DataFrame = df.filter(pl.col('team') == team)
        seasons: list[int] = list(set(t_df['season']))
        seasons.sort()

        # First add the values which are constants.
        combined_info: dict[str] = {
                # The season column will contain each season for this data
                'season': ','.join([str(s) for s in seasons]),
        }

        for col in ['team', 'situation']:
            combined_info[col] = list(t_df[col])[0]

        # Then add the values which are sum totals for each season
        for col in ['gamesPlayed', 'iceTime', 'xGoalsFor', 'goalsFor', 'xGoalsAgainst',
                    'goalsAgainst']:
            combined_info[col] = t_df[col].sum()

        # And finally compute rate metrics from each column containing a total metric value,
        # i.e. goalsFor -> goalsForPerHour (GFph)
        for total_col, rate_col in zip(['goalsFor', 'goalsAgainst', 'xGoalsFor', 'xGoalsAgainst'],
                                       ['goalsForPerHour', 'goalsAgainstPerHour',
                                        'xGoalsForPerHour', 'xGoalsAgainstPerHour']):

            combined_info[rate_col] = combined_info[total_col] * (60.0 / combined_info['iceTime'])

        combined_info['averageIceTime'] = round(combined_info['iceTime'] /
                                                combined_info['gamesPlayed'], 2)

        team_dfs.append(pl.DataFrame(combined_info))

    final_df: pl.DataFrame = pl.concat(team_dfs)

    final_df = final_df.cast(
        {
            'gamesPlayed': pl.Int16,
            'goalsFor': pl.Int16,
            'goalsAgainst': pl.Int16,
            'xGoalsFor': pl.Float32,
            'xGoalsAgainst': pl.Float32,
        }
    )

    return final_df


def combine_skater_seasons(df: pl.DataFrame) -> pl.DataFrame:
    """
    Called when a user requests multiple seasons worth of data and wants to have them combined
    into a single row for each skater.

    Goes through the data provided by the query and combines the data for each player-season into
    one row, returning the resulting DataFrame.

    :param pl.DataFrame df: The raw results of the query containing rows for each player-season

    :return pl.DataFrame: The output DataFrame with all player-seasons combined into one row.
    """
    # This list will contain DFs for each individual player, to be concatenated at the end
    player_dfs: list[pl.DataFrame] = []

    # For each unique player, create a filtered DF of just their data and use it to create
    # a dict summarizing the info.
    for player_id in set(df['playerID']):
        p_df: pl.DataFrame = df.filter(pl.col('playerID') == player_id)
        seasons: list[int] = list(set(p_df['season']))
        seasons.sort()

        if len(seasons) == 1:
            # If the player only has one seasons worth of data in the results, just add that row
            p_df = p_df.cast({'season': pl.String})
            player_dfs.append(p_df)
            continue

        # First add the values which are constants.
        combined_info: dict[str] = {
                'playerID': player_id,
                # The season column will contain each season for this data
                'season': ','.join([str(s) for s in seasons]),
        }

        for col in ['name', 'team', 'position', 'situation']:
            combined_info[col] = list(p_df[col])[0]

        # Then add the values which are sum totals for each season
        for col in ['gamesPlayed', 'iceTime', 'points', 'goals', 'individualxGoals', 'xGoalsFor',
                    'goalsFor', 'xGoalsAgainst', 'goalsAgainst', 'penaltiesTaken',
                    'penaltiesDrawn', 'faceoffsWon', 'faceoffsLost', 'shotsBlocked',
                    'oZoneShifts', 'dZoneShifts', 'neutralZoneShifts', 'flyShifts']:
            combined_info[col] = p_df[col].sum()

        # And finally compute rate metrics from each column containing a total metric value,
        # i.e. goalsFor -> goalsForPerHour (GFph)
        for total_col, rate_col in zip(['goalsFor', 'goalsAgainst', 'xGoalsFor',
                                        'xGoalsAgainst', 'points', 'goals'],
                                        ['goalsForPerHour', 'goalsAgainstPerHour',
                                         'xGoalsForPerHour', 'xGoalsAgainstPerHour',
                                         'pointsPerHour', 'goalsPerHour']):

            combined_info[rate_col] = combined_info[total_col] * (60.0 / combined_info['iceTime'])

        combined_info['averageIceTime'] = round(combined_info['iceTime'] /
                                                combined_info['gamesPlayed'], 2)

        p = pl.DataFrame(combined_info)

        player_dfs.append(p)


    for i, p in enumerate(player_dfs[:]):
        # Make sure dataframe has columns in a consistent order before concat
        p = p[['playerID', 'season', 'name', 'team', 'position', 'situation', 'gamesPlayed',
               'iceTime', 'points', 'goals', 'individualxGoals', 'xGoalsFor', 'xGoalsAgainst',
               'goalsFor', 'goalsAgainst', 'xGoalsForPerHour', 'xGoalsAgainstPerHour',
               'goalsForPerHour', 'goalsAgainstPerHour', 'pointsPerHour', 'goalsPerHour',
               'averageIceTime', 'penaltiesTaken', 'penaltiesDrawn', 'faceoffsWon',
               'faceoffsLost', 'shotsBlocked', 'oZoneShifts', 'dZoneShifts',
               'neutralZoneShifts', 'flyShifts']]

        # Also ensure columns are of consistent types before concat
        p = p.cast(
            {
                'playerID': pl.Int32,
                'gamesPlayed': pl.Int16,
                'iceTime': pl.Float32,
                'points': pl.Int16,
                'goals': pl.Int16,
                'individualxGoals': pl.Float64,
                'goalsFor': pl.Int16,
                'goalsAgainst': pl.Int16,
                'xGoalsFor': pl.Float32,
                'xGoalsAgainst': pl.Float32,
                'pointsPerHour': pl.Float32,
                'goalsPerHour': pl.Float32,
                'goalsForPerHour': pl.Float32,
                'goalsAgainstPerHour': pl.Float32,
                'xGoalsForPerHour': pl.Float32,
                'xGoalsAgainstPerHour': pl.Float32,
                'averageIceTime': pl.Float32,
                'penaltiesTaken': pl.Int16,
                'penaltiesDrawn': pl.Int16,
                'faceoffsWon': pl.Int16,
                'faceoffsLost': pl.Int16,
                'shotsBlocked': pl.Int16,
                'oZoneShifts': pl.Int16,
                'dZoneShifts': pl.Int16,
                'neutralZoneShifts': pl.Int16,
                'flyShifts': pl.Int16
            }
        )

        player_dfs[i] = p
        with pl.Config(tbl_cols=32):
            print(player_dfs[i])

    final_df: pl.DataFrame = pl.concat(player_dfs)

    final_df = final_df.sort(by=['team', 'playerID'])

    return final_df


def combine_goalie_seasons(df: pl.DataFrame) -> pl.DataFrame:
    """
    Called when a user requests multiple seasons worth of data and wants to have them combined
    into a single row for each goalie.

    Goes through the data provided by the query and combines the data for each player-season into
    one row, returning the resulting DataFrame.

    :param pl.DataFrame df: The raw results of the query containing rows for each player-season

    :return pl.DataFrame: The output DataFrame with all player-seasons combined into one row.
    """
    # This list will contain DFs for each individual player, to be concatenated at the end
    player_dfs: list[pl.DataFrame] = []

    # For each unique player, create a filtered DF of just their data and use it to create
    # a dict summarizing the info.
    for player_id in set(df['playerID']):
        p_df: pl.DataFrame = df.filter(pl.col('playerID') == player_id)
        seasons: list[int] = list(set(p_df['season']))
        seasons.sort()

        if len(seasons) == 1:
            # If the player only has one seasons worth of data in the results, just add that row
            p_df = p_df.cast({'season': pl.String})
            player_dfs.append(p_df)
            continue

        # First add the values which are constants.
        combined_info: dict[str] = {
                'playerID': player_id,
                # The season column will contain each season for this data
                'season': ','.join([str(s) for s in seasons]),
        }

        for col in ['name', 'team', 'situation']:
            combined_info[col] = list(p_df[col])[0]

        # Then add the values which are sum totals for each season
        for col in ['gamesPlayed', 'iceTime', 'xGoals', 'goals',
                    'lowDangerShots', 'mediumDangerShots', 'highDangerShots',
                    'lowDangerxGoals', 'mediumDangerxGoals', 'highDangerxGoals',
                    'lowDangerGoals', 'mediumDangerGoals', 'highDangerGoals']:
            combined_info[col] = p_df[col].sum()

        player_dfs.append(pl.DataFrame(combined_info))

    final_df: pl.DataFrame = pl.concat(player_dfs)

    final_df = final_df.cast(
        {
            'gamesPlayed': pl.Int16,
            'iceTime': pl.Int16,
            'goals': pl.Int16,
            'xGoals': pl.Float32,
            'lowDangerShots': pl.Int16,
            'mediumDangerShots': pl.Int16,
            'highDangerShots': pl.Int16,
            'lowDangerxGoals': pl.Float32,
            'mediumDangerxGoals': pl.Float32,
            'highDangerxGoals': pl.Float32,
            'lowDangerGoals': pl.Int16,
            'mediumDangerGoals': pl.Int16,
            'highDangerGoals': pl.Int16,
        }
    )

    final_df = final_df.sort(by=['team', 'playerID'])

    return final_df
