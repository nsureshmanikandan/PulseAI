import json
import logging
import re
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.modules.ingestion.parser import parse_excel

logger = logging.getLogger(__name__)
router = APIRouter()

# Keywords that signal the user wants tabular/row-level output
_TABLE_KEYWORDS = re.compile(
    r"\b(show|list|display|give me|print|table|rows|records|entries|top\s+\d+|bottom\s+\d+|"
    r"filter|where|greater than|less than|above|below|equal to|between|who have|that have|"
    r"which loans|which rows|cross.?tab|pivot|breakdown table|group by)\b",
    re.IGNORECASE,
)


def _is_table_question(question: str) -> bool:
    return bool(_TABLE_KEYWORDS.search(question))


def _build_table_context(dfs: dict, question: str) -> str:
    """
    For table-intent questions, attempt to pre-compute the relevant
    filtered/sorted DataFrame so the LLM gets real rows to format.
    Falls back to full data sample if pandas eval fails.
    """
    import pandas as pd

    parts = []
    for tab_name, df in dfs.items():
        q_lower = question.lower()

        result_df = None

        # ── top / bottom N ──────────────────────────────────────────────
        top_match = re.search(r"top\s+(\d+).+?(?:by|sorted by|based on|ordered by)\s+([\w_]+)", question, re.I)
        bot_match = re.search(r"bottom\s+(\d+).+?(?:by|sorted by|based on|ordered by)\s+([\w_]+)", question, re.I)
        if top_match:
            n, col = int(top_match.group(1)), top_match.group(2)
            if col in df.columns:
                result_df = df.nlargest(n, col)
        elif bot_match:
            n, col = int(bot_match.group(1)), bot_match.group(2)
            if col in df.columns:
                result_df = df.nsmallest(n, col)

        # ── filter: col > / < / >= / <= value ───────────────────────────
        if result_df is None:
            filter_match = re.search(
                r"([\w_]+)\s*(>|<|>=|<=|=|==)\s*(\d+(?:\.\d+)?)", question
            )
            if filter_match:
                col, op, val = filter_match.group(1), filter_match.group(2), float(filter_match.group(3))
                op = op.replace("=", "==").replace(">>>", ">=").replace("<<<", "<=")
                if op == "===":
                    op = "=="
                if col in df.columns:
                    try:
                        mask = df[col].apply(lambda x: eval(f"{x} {op} {val}"))
                        result_df = df[mask]
                    except Exception:
                        pass

        # ── "greater than 0 / above average / below X" ──────────────────
        if result_df is None:
            gt_match = re.search(r"([\w_]+)\s+(?:greater than|above|more than)\s+(\d+(?:\.\d+)?)", q_lower)
            lt_match = re.search(r"([\w_]+)\s+(?:less than|below|fewer than)\s+(\d+(?:\.\d+)?)", q_lower)
            avg_match = re.search(r"([\w_]+)\s+(?:above|greater than|higher than)\s+average", q_lower)
            if gt_match:
                col, val = gt_match.group(1), float(gt_match.group(2))
                if col in df.columns:
                    result_df = df[df[col] > val]
            elif lt_match:
                col, val = lt_match.group(1), float(lt_match.group(2))
                if col in df.columns:
                    result_df = df[df[col] < val]
            elif avg_match:
                col = avg_match.group(1)
                if col in df.columns:
                    result_df = df[df[col] > df[col].mean()]

        # ── group-by / cross-tab ─────────────────────────────────────────
        if result_df is None:
            grp_match = re.search(r"group(?:ed)?\s+by\s+([\w_]+)", q_lower)
            xtab_match = re.search(r"([\w_]+)\s+(?:vs|versus|by|cross.?tab)\s+([\w_]+)", q_lower)
            if grp_match:
                col = grp_match.group(1)
                if col in df.columns:
                    num_cols = df.select_dtypes(include="number").columns.tolist()
                    if num_cols:
                        result_df = df.groupby(col)[num_cols].agg(["mean", "sum", "count"]).round(2).reset_index()
                    else:
                        result_df = df.groupby(col).size().reset_index(name="count")
            elif xtab_match:
                c1, c2 = xtab_match.group(1), xtab_match.group(2)
                if c1 in df.columns and c2 in df.columns:
                    try:
                        result_df = pd.crosstab(df[c1], df[c2]).reset_index()
                    except Exception:
                        pass

        # ── default: first 20 rows as fallback ──────────────────────────
        if result_df is None:
            result_df = df.head(20)

        row_count = len(result_df)
        csv_rows = result_df.head(50).to_csv(index=False)
        stats = df.describe(include="all").to_string()

        parts.append(
            f"Tab: {tab_name}\n"
            f"All columns: {', '.join(df.columns)}\n"
            f"Total rows in dataset: {len(df)}\n"
            f"Matching / relevant rows ({row_count} rows shown, capped at 50):\n{csv_rows}\n"
            f"Full dataset stats:\n{stats}"
        )

    return "\n\n---\n\n".join(parts)


def _build_analytics_context(dfs: dict) -> str:
    """Compact stats context for non-table questions."""
    parts = []
    for tab_name, df in dfs.items():
        head = df.head(5).to_csv(index=False)
        stats = df.describe(include="all").to_string()
        parts.append(
            f"Tab: {tab_name}\nColumns: {', '.join(df.columns)}\nRows: {len(df)}\n"
            f"Sample (first 5 rows):\n{head}\nStats:\n{stats}"
        )
    return "\n\n---\n\n".join(parts)


def _ask_llm(dfs: dict, question: str) -> str:
    from backend.modules.ai.llm_factory import AccentureLbpassLLM
    from backend.config import Settings

    llm = AccentureLbpassLLM(Settings())

    if _is_table_question(question):
        context = _build_table_context(dfs, question)
        prompt = (
            "You are a data analyst. The user wants tabular data. "
            "You have been given the actual relevant rows already pre-filtered from the dataset.\n\n"
            "Dataset:\n" + context + "\n\n"
            "Question: " + question + "\n\n"
            "Instructions:\n"
            "1. Output a heading line (e.g. '### Loans with Past Due Days > 0') then a blank line.\n"
            "2. Output the table as a raw GitHub-Flavored Markdown table — pipes and dashes ONLY.\n"
            "   CRITICAL: Do NOT wrap the table in triple backticks or any code fence. Output bare GFM.\n"
            "   Example of correct format:\n"
            "   | Col A | Col B |\n"
            "   |-------|-------|\n"
            "   | val1  | val2  |\n"
            "3. After the table, add a blank line then a short 2-3 sentence NLP insight (bold key numbers).\n"
            "4. Do NOT explain how you filtered — just show the table and insight.\n"
            "5. If there are more than 50 matching rows, show the top 50 and note the total count."
        )
    else:
        context = _build_analytics_context(dfs)
        prompt = (
            "You are a data analyst. Answer the following question based on the dataset below.\n\n"
            "Dataset:\n" + context + "\n\n"
            "Question: " + question + "\n\n"
            "Give a clear, concise answer. If you can compute a number, compute it. "
            "Use bullet points or bold text to highlight key findings."
        )

    raw = llm.chat(prompt)

    # Strip code-fenced tables that GPT-4o sometimes wraps in ```...```
    # so ReactMarkdown receives bare GFM table syntax
    import re as _re
    raw = _re.sub(r'```(?:markdown|md|text|csv|table)?\s*\n((?:\|.*\n?)+)\n?```', r'\1', raw)

    return raw


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
                answer = _ask_llm(dfs, question)
                await websocket.send_text(json.dumps({"answer": answer, "done": True}))
            except Exception as exc:
                logger.error(f"Chat error: {exc}", exc_info=True)
                await websocket.send_text(json.dumps({"error": f"Failed to process query: {exc}", "done": True}))

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: dataset {dataset_id}")
