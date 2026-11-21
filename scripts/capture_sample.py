"""Capture Sample AI responses from Live runs into app/sample/ai.json.

Needs Live env vars (SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PRIVATE_KEY_PATH)
and sql/setup.sql already run. Each note is a real AI_COMPLETE draft + verifier run
(saved to MARKET_SHARE_REPORTS); each answer is a real Cortex Agent call.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
import ai  # noqa: E402

out = {"notes": {}, "ask": {}}
for scope in ai.SCOPES:
    n = ai.run_note_live(scope, lambda i, s: None)
    print(scope, n["status"], len(n["edits"]), n["latency_ms"], "ms", flush=True)
    out["notes"][scope] = n
for q in ai.QUESTIONS:
    a = ai.ask_live(q, lambda i, s: None)
    print("ask", a["latency_ms"], "ms", bool(a["table"]), q[:50], flush=True)
    out["ask"][q] = a
(ROOT / "app" / "sample" / "ai.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
