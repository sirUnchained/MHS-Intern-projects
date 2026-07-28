import pandas as pd
from sqlalchemy import text
from sqlalchemy import Engine
from typing import Optional


def read(
    engine: Engine,
    table_name: str,
    columns: Optional[list] = None,
) -> pd.DataFrame:
    try:
        if columns is None:
            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}'
                      AND column_name != 'embedding'
                    ORDER BY ordinal_position;
                """))
                col_names = [row[0] for row in result]
            if not col_names:
                col_names = [
                    "date",
                    "open",
                    "high",
                    "low",
                    "close",
                    "adj_close",
                    "volume",
                ]
            select_cols = ", ".join(col_names)
        else:
            select_cols = ", ".join(columns)

        query = f"SELECT {select_cols} FROM {table_name} ORDER BY date ASC;"
        df = pd.read_sql(
            sql=query,
            con=engine,
            parse_dates=["date"],
            index_col="date",
        )
        print(f"Read {len(df)} rows from '{table_name}'")
        return df
    except Exception as e:
        print(f"Read from '{table_name}' failed: {e}")
        return pd.DataFrame()
