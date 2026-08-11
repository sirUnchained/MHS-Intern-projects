import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine
from typing import Literal


def load(
    data: pd.DataFrame,
    engine: Engine,
    table_name: str,
    if_exists: Literal["fail", "replace", "append"] = "fail",
    add_vector_column: bool = True,
) -> None:
    """
    Load DataFrame to database table.

    Args:
        data: DataFrame to write to database.
        engine: SQLAlchemy database engine.
        table_name: Target table name.
        if_exists: How to handle existing table: 'fail', 'replace', or 'append'.
        add_vector_column: If True, adds an 'embedding' vector column for ML use.
    """

    if data.empty:
        print("Empty DataFrame — nothing written.")
        return

    # Reset index -> 'Date' column, then make all column names safe for SQL:
    # - lowercase
    # - replace spaces with underscores
    df_to_write = data.reset_index()
    df_to_write.columns = df_to_write.columns.str.lower().str.replace(
        " ", "_"
    )  # "Adj Close" -> "adj_close"

    try:
        df_to_write.to_sql(
            name=table_name,
            con=engine,
            if_exists=if_exists,
            index=False,
            method="multi",
        )
        print(f"Wrote {len(df_to_write)} rows to '{table_name}'")

        if add_vector_column:
            with engine.connect() as conn:
                alter_sql = text(
                    f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS embedding vector(1536);"
                )
                conn.execute(alter_sql)
                conn.commit()
                print(f"Added 'embedding' column to '{table_name}'")

    except Exception as e:
        print(f"Write to '{table_name}' failed: {e}")
        raise
