"""AI calls: the grounded share note (AI_COMPLETE draft + AI_COMPLETE verifier) and
Ask an analyst (the MARKET_SHARE_AGENT Cortex Agent via DATA_AGENT_RUN).

Sample mode replays responses captured from Live runs (sample/ai.json) after a
4-8 s staged wait, and the UI labels them "Sample AI response".
"""
import json
import random
import time
from pathlib import Path

from data import SCHEMA, session

MODEL = "claude-sonnet-4-5"
AGENT = f"{SCHEMA}.MARKET_SHARE_AGENT"
SAMPLE_AI = Path(__file__).parent / "sample" / "ai.json"

SCOPES = {
    "ALL": "Whole book",
    "RESTAURANTS": "Restaurants & Food Service",
    "GROCERY": "Food & Beverage Stores",
    "HEALTH": "Health & Personal Care",
    "FURNITURE": "Furniture & Home Furnishings",
    "APPAREL": "Clothing & Accessories",
    "ELECTRONICS": "Electronics & Appliances",
}

QUESTIONS = [
    "Which merchant categories gained the most market share between July 2024 and June 2026?",
    "What was our average share in basis points by merchant category in 2026?",
    "Which category had the widest negative growth gap in June 2026?",
    "How much did total processed volume grow from June 2025 to June 2026?",
]

RULES = (
    "You are a payments-portfolio strategy analyst. Write a concise market-share note using ONLY the FACTS JSON.\n"
    "DATA RULES: copy every figure from the *_display fields verbatim (character for character); share is in basis points "
    "(100 bps = 1%); growth gap = book YoY growth minus market YoY growth, in percentage points (pp); status is given, do not "
    "recompute it; no estimates, no hedging words, no outside benchmarks, no causes that are not in FACTS; missing = n/d. "
    "Do not name any real bank, processor, merchant or company.\n"
    "OUTPUT markdown: start with '# ' and a title, then a one-line takeaway naming the verticals gaining and losing share, "
    "a table (vertical | processed (latest month) | market (latest month) | share start -> now | change | growth gap | status), "
    "3 bullets with what to look at next, and end with '## Data coverage' saying the months and the source view."
)


def sample_ai():
    return json.loads(SAMPLE_AI.read_text()) if SAMPLE_AI.exists() else {"notes": {}, "ask": {}}


def note_steps(scope):
    n = 6 if scope == "ALL" else 1
    return [
        f"Building the fact pack: {n} vertical{'s' if n > 1 else ''} from MARKET_SHARE_VERTICAL_SUMMARY (Jul 2024 to Jun 2026)",
        f"Drafting the note with AI_COMPLETE ({MODEL}) under the data rules",
        "Fact-checking every figure against the fact pack with a second AI_COMPLETE pass",
        "Saving the note and verdict to MARKET_SHARE_REPORTS",
    ]


ASK_STEPS = [
    "Sending the question to the Market Share Agent (DATA_AGENT_RUN)",
    "Cortex Analyst writes SQL over the MARKET_SHARE_SV semantic view",
    "Running the SQL on SNOWPACK_MARKET_SHARE_WH",
    "Composing the answer from the result set",
]


def sample_wait(on_step, steps):
    """Spread a 4-8 s jittered wait over the staged steps (Sample mode only)."""
    total = random.uniform(4.0, 8.0)
    for i, s in enumerate(steps):
        on_step(i, s)
        time.sleep(total / len(steps))


# ------------------------------------------------------------------ share note (Live)
def fact_pack(scope):
    where = "" if scope == "ALL" else "WHERE category_code = ?"
    params = [] if scope == "ALL" else [scope]
    raw = session().sql(f"""
        SELECT ARRAY_AGG(OBJECT_CONSTRUCT(
          'vertical', category_name, 'status', status,
          'latest_month', latest_month::string,
          'processed_latest_display', '$' || TO_CHAR(ROUND(processed_latest_usd / 1e6, 1), '999,990.0') || 'M',
          'market_latest_display', '$' || TO_CHAR(ROUND(market_latest_usd / 1e9, 2), '990.00') || 'B',
          'share_start_display', TO_CHAR(share_start_bps, '990.0') || ' bps',
          'share_now_display', TO_CHAR(share_now_bps, '990.0') || ' bps',
          'share_change_display', IFF(share_change_bps >= 0, '+', '') || TRIM(TO_CHAR(share_change_bps, '990.0')) || ' bps',
          'book_yoy_display', IFF(book_yoy_pct >= 0, '+', '') || TRIM(TO_CHAR(book_yoy_pct, '990.0')) || '%',
          'market_yoy_display', IFF(market_yoy_pct >= 0, '+', '') || TRIM(TO_CHAR(market_yoy_pct, '990.0')) || '%',
          'growth_gap_display', IFF(growth_gap_pp >= 0, '+', '') || TRIM(TO_CHAR(growth_gap_pp, '990.0')) || ' pp'
        )) WITHIN GROUP (ORDER BY share_change_bps DESC)
        FROM {SCHEMA}.MARKET_SHARE_VERTICAL_SUMMARY {where}
    """, params=params).collect()[0][0]
    rows = json.loads(raw)
    for r in rows:
        for k, v in r.items():
            if isinstance(v, str):
                r[k] = " ".join(v.split()).replace("$ ", "$")
    return {"window": "Jul 2024 to Jun 2026 (share start/now are 3-month averages)",
            "source": "SNOWPACK_MARKET_SHARE.CORE.MARKET_SHARE_VERTICAL_SUMMARY", "verticals": rows}


def complete(prompt):
    raw = session().sql("SELECT AI_COMPLETE(?, ?)", params=[MODEL, prompt]).collect()[0][0]
    # The string result can arrive JSON-encoded ("..." with escapes); decode it once.
    if isinstance(raw, str) and raw.startswith('"'):
        try:
            raw = json.loads(raw)
        except ValueError:
            pass
    return raw.strip()


def draft_note(fp):
    return complete(RULES + f"\n\nFACTS: {json.dumps(fp)}")


def _last_json(text):
    dec, out, i = json.JSONDecoder(), None, 0
    while True:
        j = text.find("{", i)
        if j < 0:
            return out
        try:
            obj, end = dec.raw_decode(text, j)
            if isinstance(obj, dict):
                out = obj
            i = end
        except ValueError:
            i = j + 1


def verify(fp, draft):
    vp = (
        "You are a fact-checker. Compare the DRAFT against the FACTS JSON (the only allowed source). Return ONLY a JSON object "
        "with keys, in this order: reason (one sentence), residual_hedges (int: count of hedge words such as likely, approximately, "
        "around, could, may), edits (array of strings, each naming one unsupported, wrong or hedged claim), "
        "status ('verified' if edits is empty and residual_hedges is 0, else 'needs_review'). "
        "Compare figures with the *_display values character for character; the same figure written with the same rounding counts "
        "as supported. Recommendations about what to look at next are allowed if they cite only FACTS figures.\n\n"
        f"FACTS: {json.dumps(fp)}\n\nDRAFT:\n{draft}"
    )
    v = _last_json(complete(vp)) or {"edits": ["The verifier output could not be parsed."], "residual_hedges": None}
    edits = v.get("edits") or []
    v["edits"] = edits
    v["status"] = "verified" if not edits and not v.get("residual_hedges") else "needs_review"
    return v


def save_note(scope, draft, v, fp, latency_ms):
    session().sql(
        f"""INSERT INTO {SCHEMA}.MARKET_SHARE_REPORTS
            (subject, scope, draft_md, report_md, status, edits_applied, residual_hedges, edits, fact_pack, model, latency_ms)
            SELECT ?, ?, ?, ?, ?, ?, ?, PARSE_JSON(?), PARSE_JSON(?), ?, ?""",
        params=[SCOPES[scope], scope, draft, draft, v["status"], len(v["edits"]), v.get("residual_hedges"),
                json.dumps(v["edits"]), json.dumps(fp), MODEL, latency_ms],
    ).collect()


def run_note_live(scope, on_step):
    t0 = time.time()
    steps = note_steps(scope)
    on_step(0, steps[0])
    fp = fact_pack(scope)
    on_step(1, steps[1])
    draft = draft_note(fp)
    on_step(2, steps[2])
    v = verify(fp, draft)
    latency = int((time.time() - t0) * 1000)
    on_step(3, steps[3])
    save_note(scope, draft, v, fp, latency)
    return {"scope": scope, "subject": SCOPES[scope], "markdown": draft, "status": v["status"],
            "edits": v["edits"], "residual_hedges": v.get("residual_hedges"), "reason": v.get("reason"),
            "fact_pack": fp, "model": MODEL, "latency_ms": latency}


# ------------------------------------------------------------------ ask an analyst (Live)
def parse_agent(raw):
    """Final answer = text and table blocks after the last tool block; SQL from the tool result."""
    j = json.loads(raw) if isinstance(raw, str) else raw
    content = j.get("content", [])
    last_tool = max([i for i, b in enumerate(content) if b.get("type") in ("tool_use", "tool_result")], default=-1)
    text, table, sql = [], None, None
    for b in content:
        if b.get("type") == "tool_result":
            for c in b["tool_result"].get("content", []):
                if isinstance(c.get("json"), dict) and c["json"].get("sql"):
                    sql = c["json"]["sql"]
                    rs = c["json"].get("result_set")
                    if rs and table is None:
                        cols = [x["name"] for x in rs.get("resultSetMetaData", {}).get("rowType", [])]
                        table = {"columns": cols, "rows": rs.get("data", [])}
    for b in content[last_tool + 1:]:
        if b.get("type") == "text":
            text.append(b["text"])
        elif b.get("type") == "table":
            rs = b["table"].get("result_set", {})
            cols = [c["name"] for c in rs.get("resultSetMetaData", {}).get("rowType", [])]
            table = {"columns": cols, "rows": rs.get("data", [])}
    return {"text": "\n\n".join(text).strip(), "sql": sql, "table": table}


def ask_live(question, on_step):
    t0 = time.time()
    on_step(0, ASK_STEPS[0])
    body = json.dumps({"messages": [{"role": "user", "content": [{"type": "text", "text": question}]}], "stream": False})
    raw = session().sql("SELECT SNOWFLAKE.CORTEX.DATA_AGENT_RUN(?, ?)", params=[AGENT, body]).collect()[0][0]
    for i in (1, 2, 3):
        on_step(i, ASK_STEPS[i])
    out = parse_agent(raw)
    out.update({"question": question, "latency_ms": int((time.time() - t0) * 1000)})
    return out
