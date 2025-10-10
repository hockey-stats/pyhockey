import polars as pl

from util.db_connect import create_connection
from util.query_builder import construct_query


def skater_summaries(season: int | list[int],
                     team: str | list[str] = 'ALL',
                     min_icetime: int = 0,
                     combine_seasons: bool = False
                     ) -> pl.DataFrame:

    