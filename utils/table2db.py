import fire
import pandas as pd
from sqlalchemy import create_engine


def table2db(table_file,
             db_table,
             table_sep=',',
             db="wheatDB",
             user="wheatdb",
             password="wheatdb"):
    engine = create_engine(
        f"mysql+pymysql://{user}:{password}@localhost:3306/{db}", echo=True)
    df = pd.read_csv(table_file, sep=table_sep)
    df.to_sql(db_table,
              engine,
              chunksize=10000,
              index=False,
              if_exists='append')


if __name__ == "__main__":
    fire.Fire(table2db)