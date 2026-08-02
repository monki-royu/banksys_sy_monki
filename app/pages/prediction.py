"""在线预测页面 — 点选表单输入客户信息，实时预测认购结果。"""

from __future__ import annotations

import pathlib
import sys
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.data_loader import (
    NUMERICAL_COLUMNS,
)
from model.predict import load_model, predict_single

# ── 字段显示名映射 ─────────────────────────────────────────────────
FIELD_LABELS: dict[str, str] = {
    "age": "年龄",
    "job": "职业",
    "marital": "婚姻状况",
    "education": "教育水平",
    "default": "是否有违约记录",
    "housing": "是否有住房贷款",
    "loan": "是否有个人贷款",
    "contact": "联系方式",
    "month": "最后联系月份",
    "day_of_week": "最后联系星期",
    "duration": "最后通话时长(秒)",
    "campaign": "本次营销联系次数",
    "pdays": "上次联系间隔天数",
    "previous": "历史联系次数",
    "poutcome": "上次营销结果",
    "emp_var_rate": "就业变动率",
    "cons_price_index": "消费者物价指数",
    "cons_conf_index": "消费者信心指数",
    "lending_rate3m": "3月贷款利率",
    "nr_employed": "就业人数",
}

# ── 分类字段的可选值 ──────────────────────────────────────────────
CATEGORY_OPTIONS: dict[str, list[str]] = {
    "job": [
        "admin.",
        "blue-collar",
        "entrepreneur",
        "housemaid",
        "management",
        "retired",
        "self-employed",
        "services",
        "student",
        "technician",
        "unemployed",
        "unknown",
    ],
    "marital": ["divorced", "married", "single", "unknown"],
    "education": [
        "basic.4y",
        "basic.6y",
        "basic.9y",
        "high.school",
        "illiterate",
        "professional.course",
        "university.degree",
        "unknown",
    ],
    "default": ["no", "yes", "unknown"],
    "housing": ["no", "yes", "unknown"],
    "loan": ["no", "yes", "unknown"],
    "contact": ["cellular", "telephone"],
    "month": [
        "jan",
        "feb",
        "mar",
        "apr",
        "may",
        "jun",
        "jul",
        "aug",
        "sep",
        "oct",
        "nov",
        "dec",
    ],
    "day_of_week": ["mon", "tue", "wed", "thu", "fri"],
    "poutcome": ["failure", "nonexistent", "success"],
}


def show_prediction() -> None:
    st.title("🎯 在线预测")
    st.markdown("输入客户信息，预测该客户是否会认购定期存款。")

    pipeline, features_meta = load_model()

    if pipeline is None:
        _show_model_not_ready()
        return

    # 显示模型信息
    _show_model_info(features_meta)

    # 构建表单
    st.subheader("客户信息录入")
    input_data = _build_form()

    if st.button("🔮 预测", type="primary", use_container_width=True):
        _do_prediction(pipeline, features_meta, input_data)


def _show_model_not_ready() -> None:
    """模型未就绪时显示引导信息。"""
    st.warning("⚠️ **模型未就绪**")
    st.markdown("""
    预测系统需要先离线训练模型才能使用。请运行以下命令：

    ```bash
    python model/train.py
    ```

    训练完成后刷新本页面即可使用预测功能。
    """)
    # 即使没有模型，也展示数据预览供参考
    _show_data_preview()


def _show_data_preview() -> None:
    """展示数据样例供无模型时参考。"""
    df = st.session_state.get("df")
    if df is not None:
        with st.expander("📋 数据样例参考"):
            st.dataframe(df.head(10), use_container_width=True, hide_index=True)


def _show_model_info(features_meta: dict) -> None:
    """展示已加载模型的训练信息。"""
    with st.expander("📦 模型信息", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("训练样本", f"{features_meta.get('training_samples', 'N/A'):,}")
        with col2:
            st.metric("AUC", features_meta.get("auc", "N/A"))
        with col3:
            st.metric("F1 Score", features_meta.get("f1", "N/A"))


def _build_form() -> dict[str, Any]:
    """构建点选输入表单，返回用户输入字典。"""
    col1, col2 = st.columns(2)
    input_data: dict[str, Any] = {}

    with col1:
        st.markdown("**基本信息**")
        input_data["age"] = st.number_input(
            FIELD_LABELS["age"], min_value=18, max_value=100, value=35, step=1
        )
        input_data["job"] = st.selectbox(FIELD_LABELS["job"], CATEGORY_OPTIONS["job"])
        input_data["marital"] = st.selectbox(
            FIELD_LABELS["marital"], CATEGORY_OPTIONS["marital"]
        )
        input_data["education"] = st.selectbox(
            FIELD_LABELS["education"], CATEGORY_OPTIONS["education"]
        )
        input_data["default"] = st.radio(
            FIELD_LABELS["default"], CATEGORY_OPTIONS["default"], horizontal=True
        )
        input_data["housing"] = st.radio(
            FIELD_LABELS["housing"], CATEGORY_OPTIONS["housing"], horizontal=True
        )
        input_data["loan"] = st.radio(
            FIELD_LABELS["loan"], CATEGORY_OPTIONS["loan"], horizontal=True
        )

    with col2:
        st.markdown("**联系信息**")
        input_data["contact"] = st.selectbox(
            FIELD_LABELS["contact"], CATEGORY_OPTIONS["contact"]
        )
        input_data["month"] = st.selectbox(
            FIELD_LABELS["month"], CATEGORY_OPTIONS["month"]
        )
        input_data["day_of_week"] = st.selectbox(
            FIELD_LABELS["day_of_week"], CATEGORY_OPTIONS["day_of_week"]
        )
        input_data["duration"] = st.number_input(
            FIELD_LABELS["duration"], min_value=0, max_value=10000, value=180, step=10
        )
        input_data["campaign"] = st.number_input(
            FIELD_LABELS["campaign"], min_value=1, max_value=100, value=1, step=1
        )
        input_data["pdays"] = st.number_input(
            FIELD_LABELS["pdays"], min_value=0, max_value=1000, value=999, step=1
        )
        input_data["previous"] = st.number_input(
            FIELD_LABELS["previous"], min_value=0, max_value=100, value=0, step=1
        )
        input_data["poutcome"] = st.selectbox(
            FIELD_LABELS["poutcome"], CATEGORY_OPTIONS["poutcome"]
        )

    with st.expander("📈 宏观经济指标（可选调整）"):
        eco_col1, eco_col2 = st.columns(2)
        with eco_col1:
            input_data["emp_var_rate"] = st.slider(
                FIELD_LABELS["emp_var_rate"], -4.0, 2.0, 0.1, step=0.1
            )
            input_data["cons_price_index"] = st.slider(
                FIELD_LABELS["cons_price_index"], 88.0, 98.0, 93.0, step=0.1
            )
        with eco_col2:
            input_data["cons_conf_index"] = st.slider(
                FIELD_LABELS["cons_conf_index"], -50.0, -30.0, -40.0, step=0.1
            )
            input_data["lending_rate3m"] = st.slider(
                FIELD_LABELS["lending_rate3m"], 0.0, 6.0, 2.0, step=0.1
            )
            input_data["nr_employed"] = st.slider(
                FIELD_LABELS["nr_employed"], 4800.0, 5300.0, 5000.0, step=1.0
            )

    return input_data


def _do_prediction(pipeline, features_meta: dict, input_data: dict[str, Any]) -> None:
    """执行预测并展示结果。"""
    with st.spinner("正在预测…"):
        result = predict_single(pipeline, features_meta, input_data)

    # ── 预测结果 ──────────────────────────────────────────────────
    st.subheader("预测结果")

    is_subscribe = result["prediction"] == "yes"
    color = "#2E86AB" if is_subscribe else "#A23B72"
    label = (
        "✅ 该客户**会认购**定期存款"
        if is_subscribe
        else "❌ 该客户**不会认购**定期存款"
    )

    st.markdown(
        f"""
        <div style="
            padding: 2rem;
            border-radius: 10px;
            background-color: {color}22;
            border: 2px solid {color};
            text-align: center;
        ">
            <h2 style="color: {color}; margin: 0;">{label}</h2>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">
                认购概率: <strong>{result["probabilities"]["yes"]:.1%}</strong>
            </p>
            <p style="margin: 0;">置信度: {result["confidence"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── 概率条形图 ──────────────────────────────────────────────────
    st.subheader("概率对比")
    prob_df = pd.DataFrame(
        {
            "结果": ["认购", "不认购"],
            "概率": [result["probabilities"]["yes"], result["probabilities"]["no"]],
        }
    )
    fig = px.bar(
        prob_df,
        x="结果",
        y="概率",
        color="结果",
        color_discrete_map={"认购": "#2E86AB", "不认购": "#A23B72"},
        text_auto=".0%",
        range_y=[0, 1],
    )
    fig.update_layout(showlegend=False, height=300)
    st.plotly_chart(fig, use_container_width=True)

    # ── 特征对比雷达图 ──────────────────────────────────────────
    _show_feature_comparison(input_data)


def _show_feature_comparison(input_data: dict[str, Any]) -> None:
    """将当前输入与认购/未认购客户群体均值进行对比。"""
    df = st.session_state.get("df")
    if df is None:
        return

    st.subheader("客户特征对比")

    # 计算认购与未认购群体的数值字段均值
    numeric_fields = [c for c in NUMERICAL_COLUMNS if c in df.columns]

    subscribe_group = df[df["subscribe"] == "yes"][numeric_fields].mean()
    not_subscribe_group = df[df["subscribe"] == "no"][numeric_fields].mean()

    # 标准化以便在同一量纲下对比
    current_values = []
    for col in numeric_fields:
        val = input_data.get(col, 0)
        col_min = df[col].min()
        col_max = df[col].max()
        if col_max > col_min:
            val_norm = (val - col_min) / (col_max - col_min)
        else:
            val_norm = 0.5
        current_values.append(round(val_norm, 3))

    sub_mean_norm = []
    not_sub_mean_norm = []
    for col in numeric_fields:
        col_min = df[col].min()
        col_max = df[col].max()
        if col_max > col_min:
            sub_mean_norm.append(
                round((subscribe_group[col] - col_min) / (col_max - col_min), 3)
            )
            not_sub_mean_norm.append(
                round((not_subscribe_group[col] - col_min) / (col_max - col_min), 3)
            )
        else:
            sub_mean_norm.append(0.5)
            not_sub_mean_norm.append(0.5)

    labels = [FIELD_LABELS.get(c, c) for c in numeric_fields]

    radar_df = pd.DataFrame(
        {
            "特征": labels * 3,
            "值": current_values + sub_mean_norm + not_sub_mean_norm,
            "群体": (
                ["当前输入"] * len(numeric_fields)
                + ["认购客户均值"] * len(numeric_fields)
                + ["未认购客户均值"] * len(numeric_fields)
            ),
        }
    )

    fig = px.line_polar(
        radar_df,
        r="值",
        theta="特征",
        color="群体",
        line_close=True,
        color_discrete_map={
            "当前输入": "#F39C12",
            "认购客户均值": "#2E86AB",
            "未认购客户均值": "#A23B72",
        },
    )
    fig.update_traces(fill="toself")
    st.plotly_chart(fig, use_container_width=True)
