"""数据概览页面 — 展示数据集概要、缺失值、统计摘要与原始数据预览。"""

from __future__ import annotations

import pandas as pd
import streamlit as st


def show_overview() -> None:
    st.title("📊 数据概览")
    st.markdown("查看银行营销数据集的整体情况。")

    df: pd.DataFrame = st.session_state["df"]

    # ── 数据概要 ──────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总样本数", f"{len(df):,}")
    with col2:
        st.metric("特征数", df.shape[1] - 2)  # exclude id and subscribe
    with col3:
        subscribe_rate = df["subscribe"].value_counts(normalize=True).get("yes", 0)
        st.metric("认购率", f"{subscribe_rate:.1%}")
    with col4:
        missing_pct = df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100
        st.metric("缺失率", f"{missing_pct:.1f}%")

    # ── 缺失值分析 ──────────────────────────────────────────────────
    st.subheader("缺失值统计")
    missing_counts = df.isnull().sum()
    missing_cols = missing_counts[missing_counts > 0]
    if len(missing_cols) > 0:
        missing_df = pd.DataFrame(
            {
                "列名": missing_cols.index,
                "缺失数量": missing_cols.values,
                "缺失比例": (missing_cols.values / len(df) * 100).round(2),
            }
        )
        st.dataframe(missing_df, use_container_width=True)
    else:
        st.success("✅ 数据集中无缺失值。")

    # ── 数值字段统计摘要 ──────────────────────────────────────────
    st.subheader("数值字段统计摘要")
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
    desc = df[numeric_cols].describe().T
    desc.columns = [c.capitalize() for c in desc.columns]
    st.dataframe(desc, use_container_width=True)

    # ── 分类字段值分布 ──────────────────────────────────────────
    st.subheader("分类字段取值概览")
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    for col in cat_cols:
        if col == "id":
            continue
        value_counts = df[col].value_counts()
        st.markdown(f"**{col}** ({len(value_counts)} 个取值)")
        st.dataframe(
            pd.DataFrame(
                {
                    "取值": value_counts.index,
                    "数量": value_counts.values,
                    "比例": (value_counts.values / len(df) * 100).round(2),
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

    # ── 原始数据预览 ──────────────────────────────────────────────
    st.subheader("原始数据预览")
    rows = st.slider("显示行数", min_value=5, max_value=100, value=10, step=5)
    st.dataframe(df.head(rows), use_container_width=True, hide_index=True)
