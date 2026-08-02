"""双变量分析页面 — 散点图与分组柱状图，支持按认购着色。"""

from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px

from app.data_loader import CATEGORICAL_COLUMNS, NUMERICAL_COLUMNS, TARGET_COLUMN


def show_bivariate() -> None:
    st.title("🔬 双变量分析")
    st.markdown("探索两个字段之间的关联，按认购结果着色。")

    df: pd.DataFrame = st.session_state["df"]

    chart_type = st.radio("图表类型", ["散点图", "分组柱状图"], horizontal=True)

    if chart_type == "散点图":
        _show_scatter(df)
    else:
        _show_grouped_bar(df)


def _show_scatter(df: pd.DataFrame) -> None:
    """散点图：X/Y 轴选择数值字段，可选颜色字段"""
    available_num = [c for c in NUMERICAL_COLUMNS if c in df.columns]

    col1, col2 = st.columns(2)
    with col1:
        x_col = st.selectbox("X 轴（数值）", available_num, index=0)
    with col2:
        y_col = st.selectbox("Y 轴（数值）", available_num, index=1)

    color_by = st.checkbox("按认购结果着色", value=True)

    fig = px.scatter(
        df.sample(min(3000, len(df)), random_state=42),
        x=x_col,
        y=y_col,
        color=TARGET_COLUMN if color_by else None,
        color_discrete_map={"yes": "#2E86AB", "no": "#A23B72"} if color_by else None,
        opacity=0.6,
        labels={x_col: x_col, y_col: y_col, TARGET_COLUMN: "是否认购"},
        title=f"{x_col} vs {y_col}",
    )
    st.plotly_chart(fig, use_container_width=True)

    # 相关性
    corr = df[[x_col, y_col]].corr().iloc[0, 1]
    st.info(f"Pearson 相关系数: **{corr:.4f}**")


def _show_grouped_bar(df: pd.DataFrame) -> None:
    """分组柱状图：分类字段分组，数值字段聚合"""
    available_cat = [c for c in CATEGORICAL_COLUMNS if c in df.columns]
    available_num = [c for c in NUMERICAL_COLUMNS if c in df.columns]

    col1, col2 = st.columns(2)
    with col1:
        cat_col = st.selectbox("分组字段（分类）", available_cat)
    with col2:
        num_col = st.selectbox("聚合数值字段", available_num, index=3)

    agg_func = st.selectbox("聚合函数", ["mean", "median", "sum", "count"], index=0)
    top_n = st.slider("显示前 N 个分组", min_value=5, max_value=20, value=10, step=5)

    # 取 top N 分组
    top_groups = df[cat_col].value_counts().head(top_n).index
    df_filtered = df[df[cat_col].isin(top_groups)]

    # 按分组 + 认购聚合
    grouped = (
        df_filtered.groupby([cat_col, TARGET_COLUMN])[num_col]
        .agg(agg_func)
        .reset_index()
    )

    fig = px.bar(
        grouped,
        x=cat_col,
        y=num_col,
        color=TARGET_COLUMN,
        barmode="group",
        color_discrete_map={"yes": "#2E86AB", "no": "#A23B72"},
        labels={
            cat_col: cat_col,
            num_col: f"{agg_func}({num_col})",
            TARGET_COLUMN: "是否认购",
        },
        title=f"{agg_func.capitalize()}({num_col}) by {cat_col}",
        text_auto=".2s",
    )
    st.plotly_chart(fig, use_container_width=True)
