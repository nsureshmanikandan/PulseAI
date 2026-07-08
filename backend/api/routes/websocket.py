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


_CHART_KEYWORDS = re.compile(
    r"\b(highest|lowest|most|least|top|bottom|average|avg|compare|comparison|"
    r"distribution|breakdown|which\s+\w+\s+has|by\s+\w+|per\s+\w+|"
    r"trend|over\s+time|month|year|rank|ranking|proportion|percentage|percent|"
    r"across|between|among)\b",
    re.IGNORECASE,
)


def _is_chart_question(question: str) -> bool:
    return bool(_CHART_KEYWORDS.search(question)) and not _is_table_question(question)


def _fuzzy_col_match(df, question_lower: str) -> tuple[list, list]:
    """
    Find which DataFrame columns are mentioned in the question.
    Uses word-boundary matching to avoid false positives like 'age' inside 'average'.
    Also does a partial-word match so 'balance' in the question matches 'outstanding_balance'.
    Returns (cat_cols_found, num_cols_found) sorted by match score desc (exact > partial).
    """
    import pandas as pd

    # Short stop-words that cause false positives even at word boundaries
    _STOP = {"id", "no", "to", "on", "at", "by", "in", "of", "or", "is", "as", "an"}

    def _score(col: str) -> int:
        col_lower = col.lower()
        needle = col_lower.replace("_", " ")
        # Exact underscore form in question e.g. "annual_income" (score 3)
        if col_lower in question_lower:
            return 3
        # Exact space form at word boundary (score 3)
        if re.search(r"\b" + re.escape(needle) + r"\b", question_lower):
            return 3
        # Plural variant — "loan types" matches "loan_type" (score 2)
        if re.search(r"\b" + re.escape(needle) + r"s?\b", question_lower):
            return 2
        if needle.endswith("s") and re.search(r"\b" + re.escape(needle[:-1]) + r"\b", question_lower):
            return 2
        # Any significant word (>3 chars) from the column name appears (score 1)
        # len>3 avoids "age" matching "average", "sum" matching "summary", etc.
        words = [w for w in needle.split() if len(w) > 3 and w not in _STOP]
        if words and any(re.search(r"\b" + re.escape(w) + r"\b", question_lower) for w in words):
            return 1
        return 0

    cat_matches, num_matches = [], []
    for col in df.columns:
        s = _score(col)
        if s > 0:
            if pd.api.types.is_numeric_dtype(df[col]):
                num_matches.append((col, s))
            else:
                cat_matches.append((col, s))

    # Sort by score desc then col length desc so best matches come first
    cat_matches.sort(key=lambda x: (x[1], len(x[0])), reverse=True)
    num_matches.sort(key=lambda x: (x[1], len(x[0])), reverse=True)
    return [c for c, _ in cat_matches], [c for c, _ in num_matches]


def _make_bar_chart(df, grp_col: str, num_col: str, title: str, agg: str = "mean", color: str = "#3b82f6") -> dict:
    import pandas as pd
    grouped = df.groupby(grp_col)[num_col].agg(agg).reset_index()
    grouped = grouped.sort_values(num_col, ascending=False).head(20)
    agg_label = "Avg" if agg == "mean" else "Total"
    return {
        "title": title,
        "data": [{
            "type": "bar",
            "x": grouped[grp_col].astype(str).tolist(),
            "y": grouped[num_col].round(2).tolist(),
            "marker": {"color": color},
        }],
        "layout": {
            "xaxis": {"title": grp_col.replace("_", " ").title()},
            "yaxis": {"title": f"{agg_label} {num_col.replace('_', ' ').title()}"},
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font": {"color": "#e2e8f0"},
        },
    }


def _build_chart_data(dfs: dict, question: str) -> dict | None:
    """
    Attempt to compute a Plotly chart config for analytical/comparison questions.
    Uses fuzzy column-name detection so natural-language column references work.
    Returns None if we can't determine an appropriate chart.
    """
    import pandas as pd

    q_lower = question.lower()
    chart_title = question.rstrip("?").strip()[:80]
    is_avg = bool(re.search(r"\b(average|avg|mean)\b", q_lower))
    is_highest = bool(re.search(r"\b(highest|most|top|largest|greatest|maximum)\b", q_lower))
    is_total = bool(re.search(r"\b(total|sum|overall)\b", q_lower))
    agg = "mean" if (is_avg or is_highest) else ("sum" if is_total else "mean")

    # Score each tab: prefer tabs where BOTH a cat and num col are mentioned (score=2),
    # then tabs with only num (score=1), then only cat (score=0.5). Pick highest.
    best_score, best_tab, best_df, best_cat, best_num = -1, None, None, [], []
    for tab_name, df in dfs.items():
        cat_cols, num_cols = _fuzzy_col_match(df, q_lower)
        score = (2 if (cat_cols and num_cols) else
                 1 if num_cols else
                 0.5 if cat_cols else 0)
        if score > best_score:
            best_score, best_tab, best_df = score, tab_name, df
            best_cat, best_num = cat_cols, num_cols

    if best_df is None or best_score == 0:
        return None

    df = best_df
    cat_cols, num_cols = best_cat, best_num

    # ── Case 1: both cat and num cols mentioned in question ─────────────────
    if cat_cols and num_cols:
        grp_col = cat_cols[0]
        num_col = num_cols[0]
        if 2 <= df[grp_col].nunique() <= 30:
            color = "#3b82f6" if agg == "mean" else "#10b981"
            return _make_bar_chart(df, grp_col, num_col, chart_title, agg, color)

    # ── Case 2: only numeric → pair with best semantic cat col ──────────────
    if num_cols and not cat_cols:
        num_col = num_cols[0]
        cat_candidates = [
            c for c in df.select_dtypes(include="object").columns
            if 2 <= df[c].nunique() <= 20
        ]
        if cat_candidates:
            hint_words = ("type", "status", "category", "tier", "class", "segment", "region", "city")
            preferred = [c for c in cat_candidates if any(h in c.lower() for h in hint_words)]
            grp_col = preferred[0] if preferred else cat_candidates[0]
            return _make_bar_chart(df, grp_col, num_col, chart_title, agg, "#8b5cf6")

    # ── Case 3: only categorical → count distribution ────────────────────────
    if cat_cols and not num_cols:
        grp_col = cat_cols[0]
        if 2 <= df[grp_col].nunique() <= 30:
            counts = df[grp_col].value_counts().reset_index()
            counts.columns = [grp_col, "count"]
            return {
                "title": chart_title,
                "data": [{
                    "type": "bar",
                    "x": counts[grp_col].astype(str).tolist(),
                    "y": counts["count"].tolist(),
                    "marker": {"color": "#f59e0b"},
                }],
                "layout": {
                    "xaxis": {"title": grp_col.replace("_", " ").title()},
                    "yaxis": {"title": "Count"},
                    "paper_bgcolor": "rgba(0,0,0,0)",
                    "plot_bgcolor": "rgba(0,0,0,0)",
                    "font": {"color": "#e2e8f0"},
                },
            }

    return None


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
                chart = _build_chart_data(dfs, question) if _is_chart_question(question) else None
                payload: dict = {"answer": answer, "done": True}
                if chart:
                    payload["chart"] = chart
                await websocket.send_text(json.dumps(payload))
            except Exception as exc:
                logger.error(f"Chat error: {exc}", exc_info=True)
                await websocket.send_text(json.dumps({"error": f"Failed to process query: {exc}", "done": True}))

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: dataset {dataset_id}")
