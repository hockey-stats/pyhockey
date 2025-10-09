import duckdb
import polars as pl

from pyhockey.util.config import MOTHERDUCK_READ_TOKEN

def main():
    
    con = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_READ_TOKEN}')

    df = con.sql("""
                 SELECT 
                    * 
                 FROM skaters 
                 WHERE 
                    team='TOR' AND
                    situation='5on5'
                 ;
                 """)

    print(df)




if __name__ == "__main__":
    main()
