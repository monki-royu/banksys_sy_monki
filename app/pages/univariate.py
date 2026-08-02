"""单变量分析页面 — 数值字段直方图 + 分类字段柱状图。"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from app.data_loader import CATEGORICAL_COLUMNS, NUMERICAL_COLUMNS, TARGET_COLUMN


def show_univariate() -> None:
    st.title("📈 单变量分析")
    st.markdown("查看每个字段的分布情况，按认购结果着色。")

    df: pd.DataFrame = st.session_state["df"]

    # ── 选择分析字段类型 ──────────────────────────────────────────
    analysis_type = st.radio("字段类型", ["数值字段", "分类字段"], horizontal=True)

    if analysis_type == "数值字段":
        _show_numeric_distributions(df)
    else:
        _show_categorical_distributions(df)


def _show_numeric_distributions(df: pd.DataFrame) -> None:
    """数值字段：直方图（按认购着色）"""
    available = [c for c in NUMERICAL_COLUMNS if c in df.columns]

    col = st.selectbox("选择数值字段", available)
    bins = st.slider("直方图分箱数", min_value=5, max_value=100, value=30, step=5)

    fig = px.histogram(
        df,
        x=col,
        color="subscribe",
        nbins=bins,
        barmode="overlay",
        opacity=0.7,
        color_discrete_map={"yes": "#2E86AB", "no": "#A23B72"},
        labels={col: col, "subscribe": "是否认购", "count": "频数"},
        title=f"{col} 分布（按认购着色）",
    )
    fig.update_layout(bargap=0.05)
    st.plotly_chart(fig, use_container_width=True)

    # 统计摘要
    st.subheader("统计指标")
    stats = df[col].describe().to_frame().T
    stats.columns = [c.capitalize() for c in stats.columns]
    stats["Skewness"] = df[col].skew().round(4)
    stats["Kurtosis"] = df[col].kurtosis().round(4)
    st.dataframe(stats, use_container_width=True)


def _show_categorical_distributions(df: pd.DataFrame) -> None:
    """分类字段：柱状图（按认购着色）"""
    available = [c for c in CATEGORICAL_COLUMNS if c in df.columns]

    col = st.selectbox("选择分类字段", available)
    top_n = st.slider("显示前 N 个取值", min_value=5, max_value=30, value=15, step=5)

    # 频率统计
    value_counts = df[col].value_counts().head(top_n).index
    df_filtered = df[df[col].isin(value_counts)]

    fig = px.histogram(
        df_filtered,
        x=col,
        color="subscribe",
        barmode="group",
        color_discrete_map={"yes": "#2E86AB", "no": "#A23B72"},
        labels={col: col, "subscribe": "是否认购", "count": "频数"},
        title=f"{col} 取值分布（按认购着色）",
        text_auto=True,
    )
    st.plotly_chart(fig, use_container_width=True)

    # 认购率表
    st.subheader("各取值认购率")
    rate_df = (
        df_filtered.groupby(col)[TARGET_COLUMN]
        .apply(lambda x: (x == "yes").mean())
        .reset_index()
    )
    rate_df.columns = [col, "认购率"]
    rate_df["认购率"] = rate_df["认购率"].map("{:.1%}".format)
    st.dataframe(rate_df, use_container_width=True, hide_index=True)
