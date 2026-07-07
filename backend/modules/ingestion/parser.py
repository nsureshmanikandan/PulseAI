import pandas as pd
from typing import Dict


def parse_excel(file_path: str) -> Dict[str, pd.DataFrame]:
    """Parse all tabs of an Excel file into a dict of DataFrames."""
    xl = pd.ExcelFile(file_path, engine="openpyxl")
    result = {}
    for sheet_name in xl.sheet_names:
        try:
            df = xl.parse(sheet_name)
            df.columns = [str(c).strip() for c in df.columns]
            result[sheet_name] = df
        except Exception:
            pass
    return result
