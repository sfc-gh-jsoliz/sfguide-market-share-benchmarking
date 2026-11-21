"""Growth gap: our YoY growth against the market's, per vertical."""
import altair as alt
import pandas as pd
import streamlit as st

import brand
from views.common import cap, cat_scale, load


def render(mode):
    df, summ = load(mode)
    latest = df.month.max()
    st.markdown(brand.header("Growth gap", "Are we growing faster than the market?",
                             "Year-over-year growth of our processed volume minus the market's, in percentage points. Positive means we take share.",
                             cap(mode, "growth_gap_pp in MARKET_SHARE_BENCHMARK"), mode != "Live"), unsafe_allow_html=True)
    s = summ.sort_values("growth_gap_pp", ascending=False).copy()
    s["short"] = s.category_name.map(brand.SHORT)
    s["side"] = ["Outgrowing the market" if x > 0 else "Lagging the market" for x in s.growth_gap_pp]
    bars = alt.Chart(s).mark_bar(cornerRadius=4, height=22).encode(
        y=alt.Y("short:N", sort=list(s.short), title=None, axis=alt.Axis(labelFontWeight=600, labelColor=brand.T["ink2"])),
        x=alt.X("growth_gap_pp:Q", title=f"Growth gap, {latest:%B %Y} (pp)", scale=alt.Scale(domain=[-9, 9])),
        color=alt.Color("side:N", scale=alt.Scale(domain=["Outgrowing the market", "Lagging the market"],
                                                 range=[brand.T["gain"], brand.T["loss"]]), title=None),
        tooltip=[alt.Tooltip("category_name:N", title="Vertical"), alt.Tooltip("book_yoy_pct:Q", title="Book YoY %", format="+.2f"),
                 alt.Tooltip("market_yoy_pct:Q", title="Market YoY %", format="+.2f"),
                 alt.Tooltip("growth_gap_pp:Q", title="Gap (pp)", format="+.2f")],
    )
    txt = alt.Chart(s).mark_text(fontSize=11, fontWeight=700, dx=alt.expr("datum.growth_gap_pp > 0 ? 18 : -18")).encode(
        y=alt.Y("short:N", sort=list(s.short)), x="growth_gap_pp:Q",
        text=alt.Text("growth_gap_pp:Q", format="+.1f"), color=alt.value(brand.T["ink2"]))
    rule = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color="#BFAFA4").encode(x="x:Q")
    c1, c2 = st.columns([1.35, 1], gap="medium")
    with c1:
        with st.container(key="card_gap"):
            st.markdown(f'<p class="ms-card-h">Growth gap by vertical</p><p class="ms-card-s">{latest:%B %Y} vs {latest.year - 1} same month</p>', unsafe_allow_html=True)
            st.altair_chart((rule + bars + txt).properties(height=300), use_container_width=True)
    with c2:
        with st.container(key="card_quad"):
            st.markdown('<p class="ms-card-h">Read-out</p><p class="ms-card-s">Where each vertical sits, from our growth and the market\'s</p>', unsafe_allow_html=True)
            def names(mask):
                n = [brand.SHORT[x] for x in s[mask].category_name]
                return ", ".join(n) if n else "None"
            quad = [
                ("Outgrowing a growing market", names((s.book_yoy_pct > 0) & (s.market_yoy_pct > 0.5) & (s.growth_gap_pp > 0)), "up"),
                ("Growing, but slower than the market", names((s.book_yoy_pct > 0) & (s.growth_gap_pp <= 0)), "flat"),
                ("Growing in a flat or shrinking market", names((s.book_yoy_pct > 0) & (s.market_yoy_pct <= 0.5) & (s.growth_gap_pp > 0)), "up"),
                ("Shrinking while the market grows", names((s.book_yoy_pct <= 0) & (s.market_yoy_pct > 0)), "down"),
            ]
            st.markdown('<div class="ms-quad">' + "".join(
                f'<div><h4 class="{c}">{brand.esc(h)}</h4><p>{brand.esc(v)}</p></div>' for h, v, c in quad) + '</div>',
                unsafe_allow_html=True)
    with st.container(key="card_trend"):
        st.markdown('<p class="ms-card-h">Growth gap over time</p><p class="ms-card-s">Monthly, from July 2025 (the first month with a year-earlier comparison)</p>', unsafe_allow_html=True)
        g = df.dropna(subset=["growth_gap_pp"])
        line = alt.Chart(g).mark_line(strokeWidth=2.2, point=alt.OverlayMarkDef(size=18)).encode(
            x=alt.X("month:T", title=None, axis=alt.Axis(format="%b %y", labelAngle=0)),
            y=alt.Y("growth_gap_pp:Q", title="Growth gap (pp)"),
            color=alt.Color("category_name:N", scale=cat_scale(), title=None),
            tooltip=[alt.Tooltip("category_name:N", title="Vertical"), alt.Tooltip("month:T", title="Month", format="%B %Y"),
                     alt.Tooltip("growth_gap_pp:Q", title="Gap (pp)", format="+.2f")])
        st.altair_chart((rule + line).properties(height=280), use_container_width=True)
