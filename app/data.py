"""Data layer: one function per dataset, Sample (bundled CSVs) or Live (Snowflake).

Sample mode computes exactly what the Snowflake views compute, from the same seeded
rows. Live never falls back to Sample: a failed query raises and the page shows it.
"""
import os
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pandas as pd
import streamlit as st

DB = "SNOWPACK_MARKET_SHARE"
SCHEMA = f"{DB}.CORE"
WAREHOUSE = "SNOWPACK_MARKET_SHARE_WH"
ROLE = "MARKET_SHARE_ROLE"
SAMPLE_DIR = Path(__file__).parent / "sample"
LIVE_ENV = ("SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PRIVATE_KEY_PATH")


def in_snowflake():
    """True when running as Streamlit in Snowflake (an active session exists)."""
    try:
        from snowflake.snowpark.context import get_active_session
        get_active_session()
        return True
    except Exception:
        return False


def live_configured():
    return in_snowflake() or all(os.environ.get(k) for k in LIVE_ENV)


@st.cache_resource(show_spinner=False)
def session():
    """Snowpark session: the app's own in Snowflake, key-pair auth when run locally."""
    if in_snowflake():
        from snowflake.snowpark.context import get_active_session
        return get_active_session()
    from snowflake.snowpark import Session
    return Session.builder.configs({
        "account": os.environ["SNOWFLAKE_ACCOUNT"],
        "user": os.environ["SNOWFLAKE_USER"],
        "authenticator": "SNOWFLAKE_JWT",
        "private_key_file": os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"],
        "role": os.environ.get("SNOWFLAKE_ROLE", ROLE),
        "warehouse": os.environ.get("SNOWFLAKE_WAREHOUSE", WAREHOUSE),
        "database": DB,
        "schema": "CORE",
    }).create()


def sql_df(q, params=None):
    df = session().sql(q, params=params or []).to_pandas()
    df.columns = [c.lower() for c in df.columns]
    return df


def r2(x):
    """Snowflake ROUND(x, 2): half away from zero."""
    if x is None or pd.isna(x):
        return None
    return float(Decimal(repr(float(x))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _benchmark_from_csv():
    c = pd.read_csv(SAMPLE_DIR / "categories.csv")
    b = pd.read_csv(SAMPLE_DIR / "book_monthly.csv")
    m = pd.read_csv(SAMPLE_DIR / "market_monthly.csv")
    df = b.merge(m, on=["category_code", "month_end"]).merge(c[["category_code", "category_name"]], on="category_code")
    df = df.sort_values(["category_code", "month_end"]).reset_index(drop=True)
    df["share_bps"] = [r2(p / s * 10000) for p, s in zip(df.processed_volume_usd, df.market_sales_usd)]
    pb = df.groupby("category_code")["processed_volume_usd"].shift(12)
    pm = df.groupby("category_code")["market_sales_usd"].shift(12)
    df["book_yoy_pct"] = [r2((a / p - 1) * 100) if pd.notna(p) else None for a, p in zip(df.processed_volume_usd, pb)]
    df["market_yoy_pct"] = [r2((a / p - 1) * 100) if pd.notna(p) else None for a, p in zip(df.market_sales_usd, pm)]
    df["growth_gap_pp"] = [r2(a - b_) if a is not None and b_ is not None else None
                           for a, b_ in zip(df.book_yoy_pct, df.market_yoy_pct)]
    return df


def _summary(df):
    rows = []
    for code, g in df.sort_values("month_end").groupby("category_code"):
        last = g.iloc[-1]
        start, now = r2(g.head(3).share_bps.mean()), r2(g.tail(3).share_bps.mean())
        chg_pct = r2((now / start - 1) * 100)
        rows.append({
            "category_code": code, "category_name": last.category_name,
            "share_start_bps": start, "share_now_bps": now, "latest_month": last.month_end,
            "processed_latest_usd": last.processed_volume_usd, "market_latest_usd": last.market_sales_usd,
            "share_latest_bps": last.share_bps, "book_yoy_pct": last.book_yoy_pct,
            "market_yoy_pct": last.market_yoy_pct, "growth_gap_pp": last.growth_gap_pp,
            "active_merchants": last.active_merchants,
            "share_change_bps": r2(now - start), "share_change_pct": chg_pct,
            "status": "Gaining" if chg_pct >= 3 else ("Losing" if chg_pct <= -3 else "Holding"),
        })
    return pd.DataFrame(rows)


NUM = ("processed_volume_usd", "market_sales_usd", "share_bps", "book_yoy_pct", "market_yoy_pct",
       "growth_gap_pp", "txn_count", "active_merchants")


@st.cache_data(show_spinner=False, ttl=600)
def benchmark(mode):
    """Vertical x month benchmark (MARKET_SHARE_BENCHMARK in Live)."""
    if mode == "Live":
        df = sql_df(f"""SELECT category_code, category_name, month_end::string AS month_end, processed_volume_usd,
                               market_sales_usd, share_bps, book_yoy_pct, market_yoy_pct, growth_gap_pp,
                               txn_count, active_merchants
                        FROM {SCHEMA}.MARKET_SHARE_BENCHMARK ORDER BY category_code, month_end""")
        for col in NUM:
            df[col] = pd.to_numeric(df[col])
    else:
        df = _benchmark_from_csv()
    df["month"] = pd.to_datetime(df["month_end"])
    return df.reset_index(drop=True)


@st.cache_data(show_spinner=False, ttl=600)
def summary(mode):
    """One row per vertical (MARKET_SHARE_VERTICAL_SUMMARY in Live)."""
    if mode == "Live":
        df = sql_df(f"""SELECT category_code, category_name, share_start_bps, share_now_bps, latest_month::string AS latest_month,
                               processed_latest_usd, market_latest_usd, share_latest_bps, book_yoy_pct, market_yoy_pct,
                               growth_gap_pp, active_merchants, share_change_bps, share_change_pct, status
                        FROM {SCHEMA}.MARKET_SHARE_VERTICAL_SUMMARY""")
        for col in df.columns:
            if col not in ("category_code", "category_name", "latest_month", "status"):
                df[col] = pd.to_numeric(df[col])
    else:
        df = _summary(_benchmark_from_csv())
    return df.sort_values("share_change_bps", ascending=False).reset_index(drop=True)


def portfolio(df):
    """Whole-book monthly totals and share."""
    p = df.groupby("month", as_index=False)[["processed_volume_usd", "market_sales_usd"]].sum()
    p["share_bps"] = p.processed_volume_usd / p.market_sales_usd * 10000
    return p


@st.cache_data(show_spinner=False, ttl=20)
def saved_notes(mode):
    if mode != "Live":
        return None
    return sql_df(f"""SELECT run_id, subject, scope, status, edits_applied, residual_hedges, report_md, edits,
                             fact_pack, model, latency_ms, created_at::string AS created_at
                      FROM {SCHEMA}.MARKET_SHARE_REPORTS ORDER BY created_at DESC LIMIT 24""")
