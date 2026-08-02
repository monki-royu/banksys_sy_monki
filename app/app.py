"""banksys_sy_monki — 银行营销数据分析与认购预测系统入口。"""

from __future__ import annotations

import streamlit as st

from app.data_loader import load_data

# ── 页面配置（必须是第一个 streamlit 命令） ──────────────────────────
st.set_page_config(
    page_title="银行营销数据分析系统",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Health check endpoint ───────────────────────────────────────────
# Streamlit 不原生支持 /health，通过 query params 模拟
if st.query_params.get("health") == "1":
    st.write("ok")
    st.stop()

# ── Session state ───────────────────────────────────────────────────
if "data_loaded" not in st.session_state:
    with st.spinner("正在加载数据…"):
        df = load_data()
        st.session_state["df"] = df
        st.session_state["data_loaded"] = True


# ── 侧边栏导航 ──────────────────────────────────────────────────────
st.sidebar.title("🏦 银行营销分析系统")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "导航",
    ["数据概览", "单变量分析", "双变量分析", "在线预测"],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**数据说明**:基于 UCI Bank Marketing 风格数据，"
    "分析客户特征与定期存款认购的关联。"
)

# ── 页面路由 ────────────────────────────────────────────────────────
if page == "数据概览":
    from app.pages.overview import show_overview

    show_overview()
elif page == "单变量分析":
    from app.pages.univariate import show_univariate

    show_univariate()
elif page == "双变量分析":
    from app.pages.bivariate import show_bivariate

    show_bivariate()
elif page == "在线预测":
    from app.pages.prediction import show_prediction

    show_prediction()
