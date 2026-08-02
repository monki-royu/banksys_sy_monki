"""数据加载模块 — 支持真实 CSV 与合成样本回退。"""

from __future__ import annotations

import pathlib

import numpy as np
import pandas as pd

DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"
TRAIN_PATH = DATA_DIR / "train.csv"
TEST_PATH = DATA_DIR / "test.csv"


# ── 特征分类 ─────────────────────────────────────────────────────────
CATEGORICAL_COLUMNS = [
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "poutcome",
]

NUMERICAL_COLUMNS = [
    "age",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr_employed",
]

TARGET_COLUMN = "subscribe"

FEATURE_COLUMNS = CATEGORICAL_COLUMNS + NUMERICAL_COLUMNS
ALL_COLUMNS = ["id"] + FEATURE_COLUMNS + [TARGET_COLUMN]


def load_data() -> pd.DataFrame:
    """加载训练数据，不存在时生成合成样本。"""
    if TRAIN_PATH.exists():
        df = pd.read_csv(TRAIN_PATH)
        _validate_columns(df)
        return df

    return _generate_synthetic_data()


def load_test_data() -> pd.DataFrame:
    """加载测试数据（不含标签），不存在时生成合成样本。"""
    if TEST_PATH.exists():
        df = pd.read_csv(TEST_PATH)
        return df

    return _generate_synthetic_test_data()


def _validate_columns(df: pd.DataFrame) -> None:
    """检查必要列是否存在（不检查额外的列）。"""
    required = {"id", TARGET_COLUMN} | set(FEATURE_COLUMNS)
    missing = required - set(df.columns)
    if missing:
        msg = f"数据缺少必要列: {missing}"
        raise ValueError(msg)


def _generate_synthetic_data(n_samples: int = 2000, seed: int = 42) -> pd.DataFrame:
    """生成合成银行营销数据用于演示。"""
    rng = np.random.default_rng(seed)

    data = {
        "id": range(1, n_samples + 1),
        "age": rng.integers(18, 95, n_samples),
        "job": rng.choice(
            [
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
            n_samples,
        ),
        "marital": rng.choice(["divorced", "married", "single", "unknown"], n_samples),
        "education": rng.choice(
            [
                "basic.4y",
                "basic.6y",
                "basic.9y",
                "high.school",
                "illiterate",
                "professional.course",
                "university.degree",
                "unknown",
            ],
            n_samples,
        ),
        "default": rng.choice(["no", "yes", "unknown"], n_samples, p=[0.8, 0.1, 0.1]),
        "housing": rng.choice(["no", "yes", "unknown"], n_samples, p=[0.4, 0.5, 0.1]),
        "loan": rng.choice(["no", "yes", "unknown"], n_samples, p=[0.7, 0.2, 0.1]),
        "contact": rng.choice(["cellular", "telephone"], n_samples, p=[0.7, 0.3]),
        "month": rng.choice(
            [
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
            n_samples,
        ),
        "day_of_week": rng.choice(["mon", "tue", "wed", "thu", "fri"], n_samples),
        "duration": rng.integers(0, 5000, n_samples),
        "campaign": rng.integers(1, 50, n_samples),
        "pdays": rng.integers(0, 1000, n_samples),
        "previous": rng.integers(0, 50, n_samples),
        "poutcome": rng.choice(
            ["failure", "nonexistent", "success"], n_samples, p=[0.2, 0.6, 0.2]
        ),
        "emp_var_rate": rng.uniform(-3.4, 1.4, n_samples).round(2),
        "cons_price_index": rng.uniform(88.0, 98.0, n_samples).round(2),
        "cons_conf_index": rng.uniform(-50.0, -30.0, n_samples).round(2),
        "lending_rate3m": rng.uniform(0.5, 6.0, n_samples).round(2),
        "nr_employed": rng.uniform(4800, 5300, n_samples).round(2),
        TARGET_COLUMN: rng.choice(["yes", "no"], n_samples, p=[0.11, 0.89]),
    }

    df = pd.DataFrame(data)
    # 确保目标列是分类类型
    df[TARGET_COLUMN] = df[TARGET_COLUMN].astype("category")
    return df


def _generate_synthetic_test_data(n_samples: int = 500, seed: int = 7) -> pd.DataFrame:
    """生成合成测试数据（不含 subscribe 列）。"""
    df = _generate_synthetic_data(n_samples, seed=seed)
    df = df.drop(columns=[TARGET_COLUMN])
    return df
