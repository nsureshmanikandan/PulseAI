import os
import pandas as pd
from typing import Dict


def parse_excel(file_path: str) -> Dict[str, pd.DataFrame]:
    """Parse Excel (.xlsx/.xls) or CSV files into a dict of DataFrames.

    CSV files are returned as a single tab named after the file stem.
    Excel files return one entry per sheet.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        tab_name = os.path.splitext(os.path.basename(file_path))[0]
        df = pd.read_csv(file_path)
        df.columns = [str(c).strip() for c in df.columns]
        return {tab_name: df}

    # Excel
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
