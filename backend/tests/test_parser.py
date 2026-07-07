import pytest
import pandas as pd
from pathlib import Path
import openpyxl


@pytest.fixture
def sample_xlsx(tmp_path):
    path = tmp_path / "test.xlsx"
    wb = openpyxl.Workbook()
    ws1 = wb.active
    ws1.title = "Sales"
    ws1.append(["Date", "Product", "Revenue", "Units"])
    ws1.append(["2024-01-01", "Widget A", 1000, 10])
    ws1.append(["2024-01-02", "Widget B", 2000, 20])
    ws2 = wb.create_sheet("Costs")
    ws2.append(["Date", "Category", "Amount"])
    ws2.append(["2024-01-01", "Marketing", 500])
    wb.save(path)
    return path


def test_parse_returns_all_tabs(sample_xlsx):
    from backend.modules.ingestion.parser import parse_excel
    result = parse_excel(str(sample_xlsx))
    assert set(result.keys()) == {"Sales", "Costs"}


def test_parse_returns_dataframes(sample_xlsx):
    from backend.modules.ingestion.parser import parse_excel
    result = parse_excel(str(sample_xlsx))
    assert isinstance(result["Sales"], pd.DataFrame)
    assert len(result["Sales"]) == 2


def test_parse_preserves_columns(sample_xlsx):
    from backend.modules.ingestion.parser import parse_excel
    result = parse_excel(str(sample_xlsx))
    assert list(result["Sales"].columns) == ["Date", "Product", "Revenue", "Units"]
