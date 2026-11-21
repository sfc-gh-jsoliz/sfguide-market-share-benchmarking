"""Shared view helpers: load data with a skeleton, show Live errors (never fall back)."""
import altair as alt
import streamlit as st

import brand
import data


def load(mode):
    ph = st.empty()
    if mode == "Live" and not st.session_state.get("_loaded_live"):
        ph.markdown(brand.skeleton(), unsafe_allow_html=True)
    try:
        df, summ = data.benchmark(mode), data.summary(mode)
    except Exception as e:  # Live failure: show it, do not substitute sample data
        ph.empty()
        st.error(f"Live query failed: {e}")
        st.caption("Check that sql/setup.sql ran and your role is MARKET_SHARE_ROLE, or switch to Sample.")
        st.stop()
    if mode == "Live":
        st.session_state["_loaded_live"] = True
    ph.empty()
    return df, summ


def cap(mode, text):
    return ("Live · " if mode == "Live" else "Sample data · ") + text


def theme():
    def _t():
        return {"config": {
            "font": "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
            "view": {"stroke": None},
            "axis": {"labelColor": brand.T["muted"], "titleColor": brand.T["ink2"], "gridColor": "#EDE4DC",
                     "gridDash": [2, 3], "domainColor": brand.T["line"], "tickColor": brand.T["line"],
                     "labelFontSize": 11, "titleFontSize": 11, "titleFontWeight": 600},
            "axisX": {"grid": False},
            "legend": {"labelColor": brand.T["ink2"], "titleColor": brand.T["muted"], "labelFontSize": 11,
                       "titleFontSize": 11, "orient": "bottom", "symbolType": "circle", "columns": 3},
            "background": "transparent",
        }}
    alt.themes.register("market_share", _t)
    alt.themes.enable("market_share")


def cat_scale():
    return alt.Scale(domain=list(brand.CAT_COLORS), range=list(brand.CAT_COLORS.values()))
