"""pytest fixtures — 提供合成 DataFrame 和已训练的模型 Pipeline 供测试使用。"""

from __future__ import annotations

import pathlib
import sys

import pandas as pd
import pytest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.data_loader import _generate_synthetic_data  # noqa: E402


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """生成 500 行的合成数据用于测试分析页面。"""
    return _generate_synthetic_data(n_samples=500, seed=42)


@pytest.fixture
def small_df() -> pd.DataFrame:
    """生成 50 行的极小数据用于预测模块测试。"""
    return _generate_synthetic_data(n_samples=50, seed=7)
