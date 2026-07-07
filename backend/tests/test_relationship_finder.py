import pandas as pd
from backend.modules.ingestion.relationship_finder import find_relationships


def test_finds_exact_column_name_match():
    dfs = {
        "Orders": pd.DataFrame({"customer_id": [1, 2, 3], "amount": [100, 200, 300]}),
        "Customers": pd.DataFrame({"customer_id": [1, 2, 3], "name": ["A", "B", "C"]}),
    }
    rels = find_relationships(dfs)
    assert len(rels) == 1
    assert rels[0]["column_a"] == "customer_id"
    assert rels[0]["column_b"] == "customer_id"


def test_no_relationship_when_no_shared_columns():
    dfs = {
        "Sales": pd.DataFrame({"revenue": [100], "units": [10]}),
        "Costs": pd.DataFrame({"expense": [50], "category": ["A"]}),
    }
    rels = find_relationships(dfs)
    assert rels == []


def test_relationship_has_required_keys():
    dfs = {
        "A": pd.DataFrame({"id": [1, 2]}),
        "B": pd.DataFrame({"id": [1, 2]}),
    }
    rels = find_relationships(dfs)
    assert all(k in rels[0] for k in ["tab_a", "tab_b", "column_a", "column_b", "confidence"])
