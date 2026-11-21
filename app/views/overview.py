"""Overview: KPIs, the share ribbon, gainers and losers, and an insight line."""
import altair as alt
import pandas as pd
import streamlit as st

import brand
from views.common import cap, cat_scale, load


def ribbon(summ):
    """Slope chart: share at the start vs now (3-month averages), one line per vertical."""
    rows = []
    for _, r in summ.iterrows():
        short = brand.SHORT[r.category_name]
        rows += [{"vertical": r.category_name, "short": short, "point": "Jul–Sep 2024", "x": 0, "bps": r.share_start_bps,
                  "status": r.status, "change": r.share_change_bps},
                 {"vertical": r.category_name, "short": short, "point": "Apr–Jun 2026", "x": 1, "bps": r.share_now_bps,
                  "status": r.status, "change": r.share_change_bps}]
    d = pd.DataFrame(rows)
    # Nudge end labels apart (about 6 bps is one label height at this chart size).
    d["ly"] = d["bps"]
    for x in (0, 1):
        idx = d[d.x == x].sort_values("bps").index
        prev = None
        for i in idx:
            if prev is not None and d.at[i, "ly"] - prev < 6:
                d.at[i, "ly"] = prev + 6
            prev = d.at[i, "ly"]
    base = alt.Chart(d).encode(
        x=alt.X("point:N", sort=["Jul–Sep 2024", "Apr–Jun 2026"], title=None,
                axis=alt.Axis(labelAngle=0, labelFontWeight=700, labelColor=brand.T["ink2"], domain=False, ticks=False)),
        y=alt.Y("bps:Q", title="Share of market (bps)", scale=alt.Scale(zero=False, padding=12)),
        color=alt.Color("vertical:N", scale=cat_scale(), legend=None),
        tooltip=[alt.Tooltip("vertical:N", title="Vertical"), alt.Tooltip("point:N", title="Period"),
                 alt.Tooltip("bps:Q", title="Share (bps)", format=".1f"),
                 alt.Tooltip("change:Q", title="Change (bps)", format="+.1f"), alt.Tooltip("status:N", title="Status")],
    )
    lines = base.mark_line(point=alt.OverlayMarkDef(size=70, filled=True)).encode(
        detail="vertical:N",
        strokeWidth=alt.condition("datum.status == 'Gaining'", alt.value(3.2), alt.value(2)),
        strokeDash=alt.condition("datum.status == 'Losing'", alt.value([5, 3]), alt.value([1, 0])))
    lab_r = base.transform_filter("datum.x == 1").mark_text(align="left", dx=9, fontSize=11, fontWeight=700).encode(
        y="ly:Q", text=alt.Text("label:N")).transform_calculate(label="datum.short + '  ' + format(datum.bps, '.0f')")
    lab_l = base.transform_filter("datum.x == 0").mark_text(align="right", dx=-9, fontSize=11).encode(
        y="ly:Q", text=alt.Text("bps:Q", format=".0f"))
    return (lines + lab_r + lab_l).properties(height=330, padding={"left": 10, "right": 110, "top": 8, "bottom": 4})


def render(mode):
    df, summ = load(mode)
    sample = mode != "Live"
    latest = df.month.max()
    st.markdown(brand.header("Overview", "Where are we winning share?",
                             "Our processed volume by merchant vertical against market retail sales, as share in basis points (100 bps = 1%).",
                             cap(mode, "MARKET_SHARE_VERTICAL_SUMMARY view"), sample), unsafe_allow_html=True)

    p = df.groupby("month", as_index=False)[["processed_volume_usd", "market_sales_usd"]].sum()
    p["bps"] = p.processed_volume_usd / p.market_sales_usd * 1e4
    now, yr = p.iloc[-1], p.iloc[-13]
    s3, n3 = p.head(3).bps.mean(), p.tail(3).bps.mean()
    gaining = int((summ.status == "Gaining").sum())
    wide = summ.loc[summ.growth_gap_pp.abs().idxmax()]
    vol_yoy = now.processed_volume_usd / yr.processed_volume_usd - 1
    kpis = "".join([
        brand.kpi("Book share of market", f"{brand.n(n3, 1)}<small>bps</small>",
                  brand.arrow(n3 - s3, f"{brand.n(n3 - s3, 1, True)} bps vs Jul–Sep 2024"), list(p.bps.round(2))),
        brand.kpi(f"Processed · {latest:%b %Y}", f"{brand.usd(now.processed_volume_usd)}",
                  brand.arrow(vol_yoy, f"{brand.n(vol_yoy * 100, 1, True)}% year over year"), list(p.processed_volume_usd / 1e9), "#5B6B7A"),
        brand.kpi("Verticals gaining share", brand.counter(gaining, f" of {len(summ)}"),
                  f'{int((summ.status == "Holding").sum())} holding · {int((summ.status == "Losing").sum())} losing'),
        brand.kpi("Widest growth gap", f"{brand.n(wide.growth_gap_pp, 1, True)}<small>pp</small>",
                  f"{brand.esc(brand.SHORT[wide.category_name])}: book {brand.n(wide.book_yoy_pct, 1, True)}% vs market {brand.n(wide.market_yoy_pct, 1, True)}%"),
    ])
    st.markdown(f'<div class="ms-kpis">{kpis}</div>', unsafe_allow_html=True)

    top, bot = summ.iloc[0], summ.iloc[-1]
    st.markdown(
        f'<div class="ms-insight"><b>{brand.esc(top.category_name)}</b> added the most share '
        f'({brand.n(top.share_change_bps, 1, True)} bps, growing {brand.n(top.book_yoy_pct, 1, True)}% against a market at {brand.n(top.market_yoy_pct, 1, True)}%). '
        f'<b>{brand.esc(bot.category_name)}</b> gave back {brand.n(abs(bot.share_change_bps), 1)} bps: our book fell '
        f'{brand.n(abs(bot.book_yoy_pct), 1)}% while the market grew {brand.n(bot.market_yoy_pct, 1, True)}%.</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([1.55, 1], gap="medium")
    with c1:
        with st.container(key="card_ribbon"):
            st.markdown('<p class="ms-card-h">Share ribbon</p><p class="ms-card-s">Share of each vertical\'s market, first quarter of the window vs the latest (3-month averages). Solid thick = gaining, dashed = losing.</p>', unsafe_allow_html=True)
            st.altair_chart(ribbon(summ), use_container_width=True)
    with c2:
        with st.container(key="card_rank"):
            st.markdown('<p class="ms-card-h">Gainers and losers</p><p class="ms-card-s">Change in share, bps, Jul–Sep 2024 to Apr–Jun 2026</p>', unsafe_allow_html=True)
            m = summ.share_change_bps.abs().max()
            items = []
            for _, r in summ.iterrows():
                w = abs(r.share_change_bps) / m * 50
                left = 50 if r.share_change_bps >= 0 else 50 - w
                col = brand.T["gain"] if r.share_change_bps >= 0 else brand.T["loss"]
                items.append(
                    f'<li><span class="nm">{brand.esc(r.category_name)} {brand.pill(r.status)}</span>'
                    f'<span class="n {"up" if r.share_change_bps >= 0 else "down"}">{brand.n(r.share_change_bps, 1, True)}</span>'
                    f'<span class="bar"><b></b><i style="left:{brand.n(left, 1)}%;width:{brand.n(w, 1)}%;background:{col}"></i></span></li>')
            st.markdown(f'<ul class="ms-rank">{"".join(items)}</ul>', unsafe_allow_html=True)
            st.markdown(f'<p class="ms-card-s" style="margin-top:.7rem">Gaining at +3% share change or more, losing at −3% or less. Latest month {latest:%B %Y}.</p>', unsafe_allow_html=True)
