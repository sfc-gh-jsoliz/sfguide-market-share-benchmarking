"""Verticals: sortable, filterable table with status pills and a detail panel."""
import altair as alt
import pandas as pd
import streamlit as st

import brand
from views.common import cap, load


def detail(df, row):
    g = df[df.category_code == row.category_code].copy()
    color = brand.CAT_COLORS[row.category_name]
    st.markdown(
        f'<p class="ms-card-h">{brand.esc(row.category_name)} {brand.pill(row.status)}</p>'
        f'<p class="ms-card-s">Share {row.share_start_bps:.1f} → {row.share_now_bps:.1f} bps ({row.share_change_bps:+.1f} bps, {row.share_change_pct:+.1f}%) · '
        f'latest growth gap {row.growth_gap_pp:+.1f} pp · {int(row.active_merchants)} active merchants</p>', unsafe_allow_html=True)
    share = alt.Chart(g).mark_line(color=color, strokeWidth=2.4, point=alt.OverlayMarkDef(size=26, color=color)).encode(
        x=alt.X("month:T", title=None, axis=alt.Axis(format="%b %y", labelAngle=0, tickCount=8)),
        y=alt.Y("share_bps:Q", title="Share (bps)", scale=alt.Scale(zero=False)),
        tooltip=[alt.Tooltip("month:T", title="Month", format="%B %Y"), alt.Tooltip("share_bps:Q", title="Share (bps)", format=".2f")],
    ).properties(height=210)
    long = pd.concat([
        pd.DataFrame({"month": g.month, "series": "Our processed volume (index)", "idx": g.processed_volume_usd / g.processed_volume_usd.iloc[0] * 100,
                      "usd": g.processed_volume_usd}),
        pd.DataFrame({"month": g.month, "series": "Market retail sales (index)", "idx": g.market_sales_usd / g.market_sales_usd.iloc[0] * 100,
                      "usd": g.market_sales_usd}),
    ])
    vol = alt.Chart(long).mark_line(strokeWidth=2.2).encode(
        x=alt.X("month:T", title=None, axis=alt.Axis(format="%b %y", labelAngle=0, tickCount=8)),
        y=alt.Y("idx:Q", title="Index, Jul 2024 = 100", scale=alt.Scale(zero=False)),
        color=alt.Color("series:N", scale=alt.Scale(domain=["Our processed volume (index)", "Market retail sales (index)"],
                                                    range=[color, brand.T["market"]]), title=None),
        strokeDash=alt.StrokeDash("series:N", scale=alt.Scale(domain=["Our processed volume (index)", "Market retail sales (index)"],
                                                              range=[[1, 0], [4, 3]]), legend=None),
        tooltip=[alt.Tooltip("month:T", title="Month", format="%B %Y"), alt.Tooltip("series:N", title="Series"),
                 alt.Tooltip("idx:Q", title="Index", format=".1f"), alt.Tooltip("usd:Q", title="USD", format="$,.0f")],
    ).properties(height=210)
    a, b = st.columns(2, gap="medium")
    with a:
        st.markdown('<p class="ms-card-s"><b>Share of market</b>, monthly</p>', unsafe_allow_html=True)
        st.altair_chart(share, use_container_width=True)
    with b:
        st.markdown('<p class="ms-card-s"><b>Growth</b>: our volume vs the market, indexed</p>', unsafe_allow_html=True)
        st.altair_chart(vol, use_container_width=True)
    t = g.sort_values("month", ascending=False)[["month_end", "processed_volume_usd", "market_sales_usd", "share_bps",
                                                 "book_yoy_pct", "market_yoy_pct", "growth_gap_pp", "txn_count"]]
    st.dataframe(t, hide_index=True, use_container_width=True, height=240, column_config={
        "month_end": "Month end",
        "processed_volume_usd": st.column_config.NumberColumn("Processed", format="$%,.0f"),
        "market_sales_usd": st.column_config.NumberColumn("Market sales", format="$%,.0f"),
        "share_bps": st.column_config.NumberColumn("Share (bps)", format="%.2f"),
        "book_yoy_pct": st.column_config.NumberColumn("Book YoY %", format="%+.2f"),
        "market_yoy_pct": st.column_config.NumberColumn("Market YoY %", format="%+.2f"),
        "growth_gap_pp": st.column_config.NumberColumn("Gap (pp)", format="%+.2f"),
        "txn_count": st.column_config.NumberColumn("Transactions", format="%,d"),
    })


def render(mode):
    df, summ = load(mode)
    st.markdown(brand.header("Verticals", "Share by merchant vertical",
                             "Sort and filter the verticals, then select a row to open its share history, growth and monthly figures.",
                             cap(mode, "MARKET_SHARE_BENCHMARK view"), mode != "Live"), unsafe_allow_html=True)
    f1, f2 = st.columns([2, 1.2])
    with f1:
        status = st.pills("Status", ["Gaining", "Holding", "Losing"], selection_mode="multi",
                          default=["Gaining", "Holding", "Losing"], key="v_status")
    with f2:
        q = st.text_input("Search verticals", placeholder="e.g. grocery", key="v_q")
    t = summ.copy()
    t = t[t.status.isin(status or [])]
    if q:
        ql = q.lower()
        t = t[t.category_name.str.lower().str.contains(ql) | t.category_code.str.lower().str.contains(ql)]
    shown = t[["category_name", "status", "share_now_bps", "share_change_bps", "processed_latest_usd",
               "market_latest_usd", "book_yoy_pct", "market_yoy_pct", "growth_gap_pp", "category_code"]].reset_index(drop=True)
    shown["status"] = shown.status.map({"Gaining": "▲ Gaining", "Holding": "● Holding", "Losing": "▼ Losing"})
    with st.container(key="card_table"):
        if shown.empty:
            st.markdown('<div class="ms-empty"><b>No verticals match</b>Clear the search or add a status filter.</div>', unsafe_allow_html=True)
            return
        ev = st.dataframe(
            shown, hide_index=True, use_container_width=True, on_select="rerun", selection_mode="single-row", key="v_table",
            column_order=["category_name", "status", "share_now_bps", "share_change_bps", "processed_latest_usd",
                          "market_latest_usd", "book_yoy_pct", "market_yoy_pct", "growth_gap_pp"],
            column_config={
                "category_name": st.column_config.TextColumn("Vertical", width="medium"),
                "status": "Status",
                "share_now_bps": st.column_config.ProgressColumn("Share now (bps)", format="%.1f", min_value=0, max_value=260),
                "share_change_bps": st.column_config.NumberColumn("Change (bps)", format="%+.1f"),
                "processed_latest_usd": st.column_config.NumberColumn("Processed, latest", format="$%,.0f"),
                "market_latest_usd": st.column_config.NumberColumn("Market, latest", format="$%,.0f"),
                "book_yoy_pct": st.column_config.NumberColumn("Book YoY %", format="%+.1f"),
                "market_yoy_pct": st.column_config.NumberColumn("Market YoY %", format="%+.1f"),
                "growth_gap_pp": st.column_config.NumberColumn("Growth gap (pp)", format="%+.1f"),
            })
        st.markdown('<p class="ms-card-s">Share now is the Apr–Jun 2026 average; change is against Jul–Sep 2024. Click a column header to sort.</p>', unsafe_allow_html=True)
    sel = ev.selection.rows if ev and ev.selection else []
    code = shown.iloc[sel[0]].category_code if sel else shown.iloc[0].category_code
    row = summ[summ.category_code == code].iloc[0]
    with st.container(key="card_detail"):
        if not sel:
            st.markdown('<p class="ms-card-s">Showing the top row. Select a row above to switch.</p>', unsafe_allow_html=True)
        detail(df, row)
