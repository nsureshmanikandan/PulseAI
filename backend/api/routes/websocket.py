import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.modules.ai.pandasai_agent import query_datalake
from backend.modules.ingestion.parser import parse_excel

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/chat/{dataset_id}")
async def websocket_chat(websocket: WebSocket, dataset_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            question = msg.get("question", "")

            if not question:
                await websocket.send_text(json.dumps({"error": "Empty question"}))
                continue

            try:
                from backend.models.db import SessionLocal, Dataset
                with SessionLocal() as db:
                    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
                    file_path = ds.blob_path if ds else None
            except Exception:
                file_path = None

            if not file_path:
                await websocket.send_text(json.dumps({"error": "Dataset not found"}))
                continue

            try:
                dfs = parse_excel(file_path)
                answer = query_datalake(dfs, question)
                await websocket.send_text(json.dumps({"answer": str(answer), "done": True}))
            except Exception as exc:
                logger.error(f"Chat error: {exc}")
                await websocket.send_text(json.dumps({"error": "Failed to process query", "done": True}))

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: dataset {dataset_id}")
