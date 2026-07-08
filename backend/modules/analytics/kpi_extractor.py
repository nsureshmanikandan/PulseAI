import pandas as pd
from typing import List, Dict, Any

# "Bad outcome" status values → red KPI
_NEG = {
    'default', 'watch', 'fraud', 'rejected', 'failed', 'at risk', 'high risk',
    'resigned', 'terminated', 'churned', 'overdue', 'late', 'delinquent',
    'cancelled', 'npa', 'written off', 'restructured', 'pending investigation',
    'flagged', 'loss', 'bad debt', 'write-off',
}
# "Good outcome" status values → green KPI
_POS = {
    'active', 'paid', 'approved', 'completed', 'good', 'excellent',
    'low risk', 'retained', 'healthy', 'on track', 'current', 'settled',
    'clear', 'hired', 'promoted', 'closed',
}

# Column name contains any of these → skip (demographic, identifier noise)
_SKIP_COL_HINTS = (
    'gender', 'sex', 'education', 'nationality', 'marital', 'race',
    'ethnicity', 'religion', 'country', 'city', 'state', 'zip', 'postal',
    'phone', 'email', 'address', 'name', '_id', '_key', '_ref', '_uuid',
    '_code', '_no ', '_serial',
)

# Semantic hints for numeric columns
_AMOUNT_HINTS = (
    'amount', 'balance', 'revenue', 'payment', 'salary', 'price',
    'value', 'income', 'total', 'outstanding', 'premium', 'payout',
    'principal', 'emi', 'refund', 'credit_limit', 'profit', 'cost',
    'fee', 'charge', 'budget',
)
_SCORE_HINTS = (
    'score', 'rating', 'index', 'utilization', 'pct', 'percent',
    'rate', 'yield', 'ratio', 'unit_price', 'per_unit', 'per_item',
    'attrition_risk',
)
_DAYS_HINTS = ('dpd', 'delay_days', 'processing_days', 'resolution_days', 'delivery_days', 'delay')
_DURATION_HINTS = ('tenure', 'age', 'duration', 'experience', 'seniority', 'years_', '_years', 'yrs')
# Columns that look like calendar year numbers — skip as KPI (not meaningful to sum/avg)
_YEAR_COL_HINTS = ('_year', 'year_', 'fiscal_year', 'review_year', 'birth_year')
_COUNT_HINTS = (
    'count', 'qty', 'quantity', 'units', 'num_', 'number_',
    'frequency', 'transactions', 'orders', 'claims', 'loans', 'enquiries',
)

# Column name patterns that signal "this is a status/category worth a rate KPI"
_STATUS_HINTS = (
    'status', 'flag', 'risk', 'outcome', 'result', 'stage',
    'type', 'category', 'tier', 'band', 'level', 'class',
)


def _col_lower(col: str) -> str:
    return col.lower()


def _matches(col: str, hints) -> bool:
    c = _col_lower(col)
    return any(h in c for h in hints)


def _should_skip(col: str) -> bool:
    c = _col_lower(col)
    return any(h in c for h in _SKIP_COL_HINTS)


def _fmt_currency(val: float) -> str:
    if abs(val) >= 1_000_000_000:
        return f"${val/1e9:.1f}B"
    if abs(val) >= 1_000_000:
        return f"${val/1e6:.1f}M"
    if abs(val) >= 1_000:
        return f"${val/1e3:.1f}K"
    return f"${val:,.0f}"


def _fmt_num(val: float) -> str:
    if abs(val) >= 1_000_000_000:
        return f"{val/1e9:.1f}B"
    if abs(val) >= 1_000_000:
        return f"{val/1e6:.1f}M"
    if abs(val) >= 1_000:
        return f"{val/1e3:.1f}K"
    if val == int(val):
        return f"{int(val):,}"
    return f"{val:,.1f}"


def _duration_unit(col: str) -> str:
    c = _col_lower(col)
    if 'year' in c or '_yr' in c or c == 'age' or c.endswith('_age'):
        return 'yrs'
    if 'month' in c or '_mo' in c or '_mth' in c:
        return 'mo'
    return 'days'


def _status_kpis(df: pd.DataFrame, seen: set) -> List[Dict]:
    kpis: List[Dict] = []
    cat_cols = [
        c for c in df.select_dtypes(include=['object', 'category']).columns
        if not _should_skip(c)
    ]
    for col in cat_cols:
        if col in seen:
            continue
        is_status = _matches(col, _STATUS_HINTS)
        nunique = df[col].nunique()
        # Only process if name looks like a status OR low cardinality (2-15)
        if not (is_status or 2 <= nunique <= 15):
            continue
        if nunique > 30:
            continue

        counts = df[col].value_counts(dropna=True)
        total = counts.sum()
        if total == 0:
            continue

        vals_lower = {str(k).lower(): k for k in counts.index}
        neg_keys = [vals_lower[v] for v in vals_lower if v in _NEG]
        pos_keys = [vals_lower[v] for v in vals_lower if v in _POS]

        if neg_keys:
            neg_n = int(counts[neg_keys].sum())
            pct = round(neg_n / total * 100, 1)
            label = " + ".join(str(k) for k in neg_keys[:2]) + " Rate"
            kpis.append({
                "id": f"{col}_neg",
                "label": label,
                "value": f"{pct}%",
                "raw": pct,
                "subtitle": f"{neg_n:,} of {total:,} {col.replace('_',' ')}",
                "type": "rate",
                "color": "red",
            })
            seen.add(col)
        elif pos_keys and is_status:
            pos_n = int(counts[pos_keys].sum())
            pct = round(pos_n / total * 100, 1)
            label = str(pos_keys[0]) + " Rate"
            kpis.append({
                "id": f"{col}_pos",
                "label": label,
                "value": f"{pct}%",
                "raw": pct,
                "subtitle": f"{pos_n:,} of {total:,} {col.replace('_',' ')}",
                "type": "rate",
                "color": "green",
            })
            seen.add(col)
    return kpis


def _numeric_kpis(df: pd.DataFrame, seen: set, limit: int) -> List[Dict]:
    kpis: List[Dict] = []
    num_cols = df.select_dtypes(include='number').columns.tolist()

    def _is_id(c: str) -> bool:
        cl = _col_lower(c)
        id_suffixes = ('_id', '_key', '_ref', '_no', '_num', '_code', '_serial', '_uuid')
        if any(cl == s.lstrip('_') or cl.endswith(s) for s in id_suffixes):
            return True
        if _matches(c, _YEAR_COL_HINTS):
            return True
        # High-cardinality check only for non-numeric columns (string IDs like phone, email)
        if df[c].dtype == object:
            nuniq = df[c].nunique()
            return nuniq > 0 and (nuniq / max(len(df), 1)) > 0.9
        return False

    for col in num_cols:
        if len(kpis) >= limit:
            break
        if col in seen or _is_id(col) or _should_skip(col):
            continue

        s = df[col].dropna()
        if len(s) == 0:
            continue
        total = float(s.sum())
        avg = float(s.mean())
        mn = float(s.min())
        mx = float(s.max())

        if _matches(col, _SCORE_HINTS):
            # score/rate checked FIRST — unit_price, discount_pct etc show avg, not sum
            kpis.append({
                "id": col,
                "label": "Avg " + col.replace('_', ' ').title(),
                "value": f"{avg:,.1f}",
                "raw": avg,
                "subtitle": f"Min {mn:,.0f}  ·  Max {mx:,.0f}",
                "type": "score",
                "color": "purple",
            })
        elif _matches(col, _AMOUNT_HINTS):
            kpis.append({
                "id": col,
                "label": col.replace('_', ' ').title(),
                "value": _fmt_currency(total),
                "raw": total,
                "subtitle": f"Avg {_fmt_currency(avg)}  ·  Max {_fmt_currency(mx)}",
                "type": "currency",
                "color": "blue",
            })
        elif _matches(col, _DAYS_HINTS):
            kpis.append({
                "id": col,
                "label": "Avg " + col.replace('_', ' ').title(),
                "value": f"{avg:.1f} days",
                "raw": avg,
                "subtitle": f"Min {mn:,.0f}  ·  Max {mx:,.0f}",
                "type": "days",
                "color": "yellow",
            })
        elif _matches(col, _DURATION_HINTS):
            unit = _duration_unit(col)
            kpis.append({
                "id": col,
                "label": "Avg " + col.replace('_', ' ').title(),
                "value": f"{avg:.1f} {unit}",
                "raw": avg,
                "subtitle": f"Min {mn:,.0f}  ·  Max {mx:,.0f}",
                "type": "days",
                "color": "yellow",
            })
        elif _matches(col, _COUNT_HINTS):
            kpis.append({
                "id": col,
                "label": col.replace('_', ' ').title(),
                "value": _fmt_num(total),
                "raw": total,
                "subtitle": f"Avg {avg:,.1f} per record",
                "type": "count",
                "color": "green",
            })
        else:
            kpis.append({
                "id": col,
                "label": col.replace('_', ' ').title(),
                "value": _fmt_num(avg),
                "raw": avg,
                "subtitle": f"Sum {_fmt_num(total)}  ·  Max {_fmt_num(mx)}",
                "type": "numeric",
                "color": "blue",
            })
        seen.add(col)

    return kpis


def extract_kpis(df: pd.DataFrame, max_kpis: int = 8) -> List[Dict[str, Any]]:
    """
    Smart business KPI extraction — works on any uploaded dataset.

    Priority:
      1. Rate KPIs from status/flag/risk/outcome columns
         (neg keywords → red; pos keywords → green)
      2. Currency totals for financial columns (amount, balance, revenue …)
      3. Averages for scores, durations, counts
    Returns up to max_kpis cards with: id, label, value, subtitle, type, color
    """
    seen: set = set()
    kpis: List[Dict] = _status_kpis(df, seen)
    remaining = max_kpis - len(kpis)
    if remaining > 0:
        kpis += _numeric_kpis(df, seen, limit=remaining)
    return kpis[:max_kpis]
