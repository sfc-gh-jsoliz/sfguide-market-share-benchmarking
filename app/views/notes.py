"""Share notes: a grounded note (AI_COMPLETE draft + verifier) and the saved-note gallery."""
import json
import time

import pandas as pd
import streamlit as st

import ai
import brand
import data
from views.common import cap


def reveal(text, ph):
    """Streaming-style reveal of the finished note."""
    shown = ""
    for i in range(0, len(text), 60):
        shown = text[: i + 60]
        ph.markdown(brand.md_safe(shown) + " ▍")
        time.sleep(0.02)
    ph.markdown(brand.md_safe(text))


def sources(fp):
    rows = fp.get("verticals", [])
    if not rows:
        return
    t = pd.DataFrame(rows)[["vertical", "share_start_display", "share_now_display", "share_change_display",
                            "growth_gap_display", "status"]]
    t.columns = ["Vertical", "Share start", "Share now", "Change", "Growth gap", "Status"]
    st.markdown(f'<div class="ms-src">Sources: fact pack from <code>{brand.esc(fp.get("source", ""))}</code>, '
                f'{brand.esc(fp.get("window", ""))}. These are the only figures the model may use.</div>', unsafe_allow_html=True)
    st.dataframe(t, hide_index=True, use_container_width=True)


def show_note(n, mode, animate=False):
    lab = ('<span class="ms-label live">Live · AI_COMPLETE</span>' if mode == "Live"
           else '<span class="ms-label">Sample AI response</span>')
    meta = f'{n.get("model", ai.MODEL)} · {n.get("latency_ms", 0) / 1000:.1f} s measured live'
    st.markdown(f'<p>{lab} {brand.verdict(n["status"])} <span class="ms-card-s">&nbsp;{brand.esc(meta)}</span></p>', unsafe_allow_html=True)
    with st.container(key=f"note_body_{n.get('scope', 'x')}"):
        ph = st.empty()
        if animate:
            reveal(n["markdown"], ph)
        else:
            ph.markdown(brand.md_safe(n["markdown"]))
    edits = n.get("edits") or []
    if edits:
        st.markdown("**Verifier flagged:**\n" + "\n".join(f"- {brand.md_safe(e)}" for e in edits))
    else:
        st.markdown(f'<p class="ms-card-s">Verifier: every figure matches the fact pack; {n.get("residual_hedges") or 0} hedge words.</p>', unsafe_allow_html=True)
    sources(n.get("fact_pack") or {})


def render(mode):
    st.markdown(brand.header("Share notes", "A share note you can defend",
                             "AI_COMPLETE drafts a one-page note from a fact pack under strict data rules; a second AI_COMPLETE pass checks every figure and marks it Verified or Needs review.",
                             cap(mode, "Cortex AI_COMPLETE · draft + verifier"), mode != "Live"), unsafe_allow_html=True)
    samples = ai.sample_ai().get("notes", {})
    with st.container(key="card_gen"):
        c1, c2 = st.columns([2, 1], vertical_alignment="bottom")
        with c1:
            scope = st.selectbox("Scope", list(ai.SCOPES), format_func=lambda k: ai.SCOPES[k], key="n_scope")
        with c2:
            go = st.button("Write share note", type="primary", use_container_width=True)
        prog = st.empty()
        if go:
            steps = ai.note_steps(scope)

            def on_step(i, s):
                prog.markdown(f'<div class="ms-card">{brand.steps_html(steps, i)}</div>', unsafe_allow_html=True)
            try:
                if mode == "Live":
                    n = ai.run_note_live(scope, on_step)
                    data.saved_notes.clear()
                else:
                    if scope not in samples:
                        raise RuntimeError("No captured sample for this scope.")
                    ai.sample_wait(on_step, steps)
                    n = samples[scope]
            except Exception as e:
                prog.empty()
                st.error(f"Note failed: {e}")
                st.stop()
            prog.markdown(f'<div class="ms-card">{brand.steps_html(steps, 4, True)}</div>', unsafe_allow_html=True)
            st.session_state["last_note"] = n
            show_note(n, mode, animate=True)
        elif st.session_state.get("last_note"):
            show_note(st.session_state["last_note"], mode)
        else:
            st.markdown('<div class="ms-empty"><b>No note yet</b>Pick the whole book or one vertical and write a note. '
                        + ("Live mode calls AI_COMPLETE twice (about 10 to 20 s)." if mode == "Live"
                           else "Sample mode replays a response captured from a Live run.") + '</div>', unsafe_allow_html=True)

    st.markdown('<p class="ms-card-h" style="margin-top:1.2rem">Saved notes</p>', unsafe_allow_html=True)
    if mode == "Live":
        try:
            saved = data.saved_notes(mode)
        except Exception as e:
            st.error(f"Live query failed: {e}")
            return
        items = [{"subject": r.subject, "status": r.status, "created": r.created_at[:16], "flagged": int(r.edits_applied or 0),
                  "markdown": r.report_md, "edits": json.loads(r.edits) if isinstance(r.edits, str) else (r.edits or []),
                  "fact_pack": json.loads(r.fact_pack) if isinstance(r.fact_pack, str) else (r.fact_pack or {}),
                  "residual_hedges": r.residual_hedges, "latency_ms": r.latency_ms or 0, "model": r.model, "scope": r.run_id[:8]}
                 for r in saved.itertuples()]
        st.markdown('<p class="ms-card-s">From MARKET_SHARE_REPORTS, newest first.</p>', unsafe_allow_html=True)
    else:
        items = [dict(n, created="Captured from Live", flagged=len(n.get("edits") or [])) for n in samples.values()]
        st.markdown('<p class="ms-card-s">Sample gallery: notes captured from Live runs, labeled as sample AI responses.</p>', unsafe_allow_html=True)
    if not items:
        st.markdown('<div class="ms-empty"><b>No saved notes</b>Notes you write appear here.</div>', unsafe_allow_html=True)
        return
    cols = st.columns(3)
    for i, n in enumerate(items):
        with cols[i % 3]:
            with st.container(key=f"card_saved_{i}"):
                title = (n["markdown"] or "").split("\n")[0].lstrip("# ").strip() or n["subject"]
                st.markdown(f'{brand.verdict(n["status"])}<p class="ms-card-h" style="margin-top:.45rem">{brand.esc(title)}</p>'
                            f'<p class="ms-card-s">{brand.esc(n["subject"])} · {brand.esc(n["created"])} · {n["flagged"]} flagged</p>',
                            unsafe_allow_html=True)
                if st.button("Open note", key=f"open_{i}", use_container_width=True):
                    st.session_state["last_note"] = n
                    st.rerun()
