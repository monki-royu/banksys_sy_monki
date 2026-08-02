"""测试数据加载模块。"""

from __future__ import annotations

from app.data_loader import (
    CATEGORICAL_COLUMNS,
    FEATURE_COLUMNS,
    NUMERICAL_COLUMNS,
    TARGET_COLUMN,
    _generate_synthetic_data,
    load_data,
)


class TestLoadData:
    def test_load_data_returns_dataframe(self):
        """AC: load_data() 返回非空的 DataFrame。"""
        df = load_data()
        assert not df.empty
        assert len(df) > 0

    def test_load_data_has_required_columns(self):
        """AC: 返回的 DataFrame 包含所有必需列。"""
        df = load_data()
        required = {"id", TARGET_COLUMN} | set(FEATURE_COLUMNS)
        assert required.issubset(set(df.columns))

    def test_load_data_target_column_values(self):
        """AC: subscribe 列只包含 'yes' 和 'no'。"""
        df = load_data()
        assert set(df[TARGET_COLUMN].unique()).issubset({"yes", "no"})


class TestSyntheticData:
    def test_default_size(self):
        """AC: 默认生成 2000 行。"""
        df = _generate_synthetic_data()
        assert len(df) == 2000

    def test_custom_size(self):
        """AC: 可指定行数。"""
        df = _generate_synthetic_data(n_samples=100)
        assert len(df) == 100

    def test_columns_structure(self):
        """AC: 合成数据包含所有特征列和目标列。"""
        df = _generate_synthetic_data()
        assert set(FEATURE_COLUMNS).issubset(set(df.columns))
        assert TARGET_COLUMN in df.columns

    def test_reproducible_seed(self):
        """AC: 相同种子生成相同数据。"""
        df1 = _generate_synthetic_data(n_samples=100, seed=42)
        df2 = _generate_synthetic_data(n_samples=100, seed=42)
        assert df1[TARGET_COLUMN].equals(df2[TARGET_COLUMN])

    def test_different_seed_different_data(self):
        """AC: 不同种子生成不同数据。"""
        df1 = _generate_synthetic_data(n_samples=100, seed=42)
        df2 = _generate_synthetic_data(n_samples=100, seed=99)
        assert not df1[TARGET_COLUMN].equals(df2[TARGET_COLUMN])

    def test_categorical_columns_are_object(self):
        """AC: 分类列是 object 或 category 类型。"""
        df = _generate_synthetic_data()
        for col in CATEGORICAL_COLUMNS:
            assert df[col].dtype in ("object", "category")

    def test_numerical_columns_are_numeric(self):
        """AC: 数值列是数值类型。"""
        df = _generate_synthetic_data()
        for col in NUMERICAL_COLUMNS:
            assert df[col].dtype in ("int64", "float64")
