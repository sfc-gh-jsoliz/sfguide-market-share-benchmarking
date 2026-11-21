"""Market Share & Vertical Benchmarking on Snowflake.

Run locally (Sample mode, no account):   streamlit run app/streamlit_app.py
Live mode locally: set SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER and SNOWFLAKE_PRIVATE_KEY_PATH
(key-pair auth) and restart. In Streamlit in Snowflake the app uses its own session.
"""
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import brand  # noqa: E402
import data  # noqa: E402
from views import ask, growth, notes, overview, verticals  # noqa: E402
from views.common import theme  # noqa: E402

st.set_page_config(page_title="Market Share & Vertical Benchmarking", page_icon="◔", layout="wide",
                   initial_sidebar_state="auto")
st.markdown(brand.CSS, unsafe_allow_html=True)
theme()

LIVE_OK = data.live_configured()
if "mode" not in st.session_state:
    st.session_state.mode = "Live" if LIVE_OK else "Sample"

VIEWS = {
    "Overview": overview.render,
    "Verticals": verticals.render,
    "Growth gap": growth.render,
    "Share notes": notes.render,
    "Ask an analyst": ask.render,
}

with st.sidebar:
    st.html(f'<div class="ms-brand">{brand.LOGO_IMG}<div><b>Market Share &amp; Vertical Benchmarking</b>'
            '<span>Payments strategy · share by merchant vertical</span></div></div>')
    st.html('<p class="ms-eyebrow">Workspace</p>')
    with st.container(key="nav"):
        view = st.radio("Section", list(VIEWS), label_visibility="collapsed", key="view")
    st.html('<p class="ms-eyebrow">Data</p>')
    with st.container(key="modes"):
        st.segmented_control("Data mode", ["Sample", "Live"], key="mode", label_visibility="collapsed",
                             help="Sample: bundled synthetic data, no account. Live: the same app on Snowflake.")
    mode = st.session_state.mode or st.session_state.get("_last_mode", "Sample")
    st.session_state["_last_mode"] = mode
    env = ('<span class="ms-env live"><i></i>Live · Snowflake</span>' if mode == "Live"
           else '<span class="ms-env sample"><i></i>Sample data</span>')
    st.html(f'<div class="ms-who"><b>Strategy analyst</b><span>Role {data.ROLE}</span><br>{env}</div>')

if mode == "Live" and not LIVE_OK:
    st.markdown(brand.header("Setup", "Connect Live mode",
                             "Live mode runs this same app on Snowflake. No connection is configured, so nothing is shown instead of falling back to sample data.",
                             "Setup needed"), unsafe_allow_html=True)
    st.markdown("1. Run `sql/setup.sql` in a Snowsight worksheet (about 15 s on an XSMALL warehouse).\n"
                "2. Register a key pair on your Snowflake user, then set these variables and restart:")
    st.code("export SNOWFLAKE_ACCOUNT=<org-account>\nexport SNOWFLAKE_USER=<YOUR_USER>\n"
            "export SNOWFLAKE_PRIVATE_KEY_PATH=~/.snowflake/keys/<your_key>.p8\n"
            "streamlit run app/streamlit_app.py", language="bash")
    st.markdown("Or deploy the app as Streamlit in Snowflake (README, *Deploy the app in Snowflake*). "
                "Switch back to **Sample** to keep exploring.")
    st.stop()

VIEWS[view](mode)
