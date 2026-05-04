from io import BytesIO
import pandas as pd


def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    """Convert a DataFrame to an in-memory Excel file."""
    buf = BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")
    buf.seek(0)
    return buf.read()
