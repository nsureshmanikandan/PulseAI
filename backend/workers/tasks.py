import logging
from typing import Any, Dict

from backend.modules.ingestion.parser import parse_excel
from backend.modules.ingestion.schema_detector import detect_schema
from backend.modules.ingestion.relationship_finder import find_relationships
from backend.modules.ai.insight_engine import extract_insights

logger = logging.getLogger(__name__)

try:
    from backend.models.db import SessionLocal
except Exception:
    SessionLocal = None


def process_upload(file_path: str, dataset_id: str) -> Dict[str, Any]:
    """
    Process an uploaded Excel file:
    1. Parse all tabs into DataFrames
    2. Detect schema per tab
    3. Find cross-tab relationships
    4. Extract insights
    5. Persist results to DB
    Returns status dict.
    """
    try:
        dfs = parse_excel(file_path)
        tab_count = len(dfs)

        schemas = {tab: {"columns": detect_schema(df), "row_count": len(df)} for tab, df in dfs.items()}
        relationships = find_relationships(dfs)

        all_insights = []
        for tab, df in dfs.items():
            insights = extract_insights(df)
            all_insights.extend(insights)

        # Persist tab profiles (best-effort — DB may not be available in all envs)
        try:
            db_session = SessionLocal()
            if hasattr(db_session, '__enter__'):
                with db_session as db:
                    _persist_results(db, dataset_id, schemas, relationships)
            else:
                db = db_session()
                try:
                    _persist_results(db, dataset_id, schemas, relationships)
                    db.commit()
                finally:
                    db.close()
        except Exception as db_err:
            logger.warning(f"DB persist skipped for {dataset_id}: {db_err}")

        return {
            "status": "completed",
            "dataset_id": dataset_id,
            "tab_count": tab_count,
            "insight_count": len(all_insights),
        }

    except Exception as exc:
        logger.error(f"process_upload failed for {dataset_id}: {exc}", exc_info=True)
        return {"status": "failed", "dataset_id": dataset_id, "error": str(exc)}


def _persist_results(db, dataset_id: str, schemas: dict, relationships: list) -> None:
    """Save tab profiles and relationships to the database."""
    import uuid
    from backend.models.db import Dataset, TabProfile, TabRelationship

    # update dataset tab_names
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if ds:
        ds.tab_names = list(schemas.keys())

    for tab_name, schema in schemas.items():
        profile = TabProfile(
            id=str(uuid.uuid4()),
            dataset_id=dataset_id,
            tab_name=tab_name,
            row_count=schema.get("row_count"),
            column_profiles=schema,
        )
        db.add(profile)

    for rel in relationships:
        db.add(TabRelationship(
            id=str(uuid.uuid4()),
            dataset_id=dataset_id,
            tab_a=rel.get("tab_a") or rel.get("from_tab", ""),
            tab_b=rel.get("tab_b") or rel.get("to_tab", ""),
            column_a=rel.get("column_a") or rel.get("from_column", ""),
            column_b=rel.get("column_b") or rel.get("to_column", ""),
            confidence=str(rel.get("confidence", "")),
        ))

    db.commit()
