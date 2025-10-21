"""
Module for handling calls to the 'goalies' table, which holds season summaries for each goalie,
divided by game state.
"""

import polars as pl

from util.db_connect import create_connection
from util.query_builder import construct_query

def goalie_summaries(season: int | list[int],
                     team: str | list[str] = 'ALL',
                     min_games_played: int = 0,
                     situation: str = 'all',
                     combine_seasons: bool = False
                     ) -> pl.DataFrame:
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

    column_mapping: dict[str] = {
        'season': season,
        'team': team,
        'situation': situation
    }

    # If getting results for all team, no need to provide a team filter in the column mapping
    if team == 'ALL':
        del column_mapping['team']

    qualifiers: dict[str] = {
        'gamesPlayed': f'>={min_games_played}'
    }

    query : str = construct_query(table_name='goalies', column_mapping=column_mapping,
                                  qualifiers=qualifiers, order_by=['team', 'season'])

    connection = create_connection()

    results: pl.DataFrame = connection.sql(query).pl()

    if combine_seasons:
        if not isinstance(season, list):
            print("The 'combine_seasons' parameter has been set to 'True', but data for only one "\
                  f"season ({season}) was requested. Returning data for just that season...")
            return results
        results: pl.DataFrame = combine_goalie_seasons(results)

    return results


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
