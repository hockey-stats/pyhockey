import polars as pl

from util.db_connect import create_connection


def skater_summaries(season: int | list[int],
                     team: str | list[str] = 'ALL',
                     min_icetime: int = 0,
                     combine_seasons: bool = False
                     ) -> pl.DataFrame:

    # First make sure values that were supplied are the correct types.
    if not isinstance(season, int):
        if isinstance(season, list):
            for value in season:
                if not isinstance(value, int):
                    raise ValueError(f"ERROR: Values provided for season must be int, "\
                                     f"received {type(value)}: {value}")
        else:
            raise ValueError(f"ERROR: Values provided for season must be int, "\
                                f"received {type(value)}: {value}")