import polars as pl

from util.db_connect import create_connection
from util.query_builder import construct_query


VALID_SITUATION_OPTIONS = ['all', '5on5', '4on5', '5on4', 'other']


def skater_summaries(season: int | list[int],
                     team: str | list[str] = 'ALL',
                     min_icetime: int = 0,
                     situation: str = 'all',
                     combine_seasons: bool = False
                     ) -> pl.DataFrame:

    if not isinstance(situation, str) and situation not in VALID_SITUATION_OPTIONS:
        raise ValueError(f"Valid options for situation are {VALID_SITUATION_OPTIONS}. \n"\
                         f"{situation} was provided. If no value is provided, defaults to 'all'.")

    query: str = construct_query(
        table_name='skaters',
        column_mapping={
            'season': season,
            'team': team,
            'situation': situation
        },
        qualifiers={
            'iceTime': f'>{min_icetime}'
        }
    )

    connection = create_connection()

    results: pl.DataFrame = connection.sql(query).pl()

    return results


def combine_seasons(df: pl.DataFrame) -> pl.DataFrame:
    seasons: set[int] = set(df['season'])

    player_dfs: list[pl.DataFrame] = []

    for player_id in set(df['playerID']):
        p_df: pl.DataFrame = df.filter(pl.col('playerID') == player_id)
        combined_info: dict[str] = {
                'playerID': player_id,
                'season': ','.join(list(set(p_df['season']))),
        }

        for col in ['name', 'team', 'position', 'situation']:
            combined_info[col] = list(p_df[col])[0]

        for col in ['gamesPlayed', 'iceTime', 'points', 'goals', 'xGoalsFor', 'goalsFor',
                    'xGoalsAgainst', 'goalsAgainst']:
            combined_info[col] = p_df[col].sum()

        # Compute rate metrics from each column containing a total metric value,
        # i.e. goalsFor -> goalsForPerHour (GFph)
        for total_col, rate_col in zip(['goalsFor', 'goalsAgainst', 'xGoalsFor',
                                        'xGoalsAgainst', 'points', 'goals'],
                                        ['goalsForPerHour', 'goalsAgainstPerHour', 'xGoalsForPerHour',
                                        'xGoalsAgainstPerHour', 'pointsPerHour', 'goalsPerHour']):

            combined_info[rate_col] = combined_info[total_col] * (60.0 / combined_info['icetime'])



if __name__ == '__main__':
    with pl.Config(tbl_cols=100, tbl_rows=100):
        print(skater_summaries(season=2024, team='TOR', min_icetime=500))
