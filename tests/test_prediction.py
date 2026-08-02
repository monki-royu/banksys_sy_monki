"""测试模型训练与预测模块。"""

from __future__ import annotations

import json
import pathlib
import sys

import joblib
from sklearn.pipeline import Pipeline

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from model.predict import load_model, predict_single  # noqa: E402
from model.train import build_preprocessing_pipeline, train  # noqa: E402


class TestTraining:
    def test_build_preprocessing_pipeline(self):
        """AC: 预处理 Pipeline 创建成功，类型正确。"""
        from sklearn.compose import ColumnTransformer

        preprocessor = build_preprocessing_pipeline()
        assert isinstance(preprocessor, ColumnTransformer)

    def test_train_returns_metrics(self):
        """AC: 训练返回包含 auc/f1/accuracy 的字典。"""
        result = train(test_size=0.3, random_state=42, n_estimators=50, max_depth=6)
        assert "auc" in result
        assert "f1" in result
        assert "accuracy" in result
        assert result["auc"] > 0.5
        assert result["f1"] > 0

    def test_train_saves_model_file(self):
        """AC: 训练后在 saved_models/ 生成 model.joblib。"""
        train(test_size=0.3, random_state=42, n_estimators=50, max_depth=6)
        model_path = PROJECT_ROOT / "model" / "saved_models" / "model.joblib"
        assert model_path.exists()

    def test_train_saves_features_json(self):
        """AC: 训练后在 saved_models/ 生成 features.json。"""
        train(test_size=0.3, random_state=42, n_estimators=50, max_depth=6)
        features_path = PROJECT_ROOT / "model" / "saved_models" / "features.json"
        assert features_path.exists()
        with open(features_path) as f:
            meta = json.load(f)
        assert "features" in meta
        assert "class_names" in meta
        assert meta["class_names"] == ["no", "yes"]

    def test_saved_model_is_pipeline(self):
        """AC: 保存的模型是 sklearn Pipeline 类型。"""
        train(test_size=0.3, random_state=42, n_estimators=50, max_depth=6)
        model_path = PROJECT_ROOT / "model" / "saved_models" / "model.joblib"
        pipeline = joblib.load(model_path)
        assert isinstance(pipeline, Pipeline)


class TestPrediction:
    def test_load_model_returns_pipeline_and_meta(self):
        """AC: load_model() 返回 (pipeline, features_meta)。"""
        pipeline, features_meta = load_model()
        assert pipeline is not None
        assert features_meta is not None
        assert "features" in features_meta

    def test_predict_single_returns_dict(self):
        """AC: predict_single() 返回包含 prediction/probability 的字典。"""
        pipeline, features_meta = load_model()
        assert pipeline is not None

        input_data = {
            "age": 35,
            "job": "admin.",
            "marital": "married",
            "education": "university.degree",
            "default": "no",
            "housing": "yes",
            "loan": "no",
            "contact": "cellular",
            "month": "may",
            "day_of_week": "mon",
            "duration": 180,
            "campaign": 1,
            "pdays": 999,
            "previous": 0,
            "poutcome": "nonexistent",
            "emp_var_rate": 0.1,
            "cons_price_index": 93.0,
            "cons_conf_index": -40.0,
            "lending_rate3m": 2.0,
            "nr_employed": 5000.0,
        }
        result = predict_single(pipeline, features_meta, input_data)
        assert "prediction" in result
        assert result["prediction"] in ("yes", "no")
        assert "probability" in result
        assert 0 <= result["probability"] <= 1
        assert "probabilities" in result
        assert "yes" in result["probabilities"]
        assert "no" in result["probabilities"]

    def test_predict_single_probabilities_sum_to_one(self):
        """AC: 预测概率之和为 1。"""
        pipeline, features_meta = load_model()
        assert pipeline is not None

        input_data = {
            "age": 30,
            "duration": 200,
            "campaign": 1,
            "pdays": 999,
            "previous": 0,
            "emp_var_rate": 0.0,
            "cons_price_index": 93.0,
            "cons_conf_index": -40.0,
            "lending_rate3m": 2.0,
            "nr_employed": 5000.0,
            "job": "admin.",
            "marital": "single",
            "education": "high.school",
            "default": "no",
            "housing": "no",
            "loan": "no",
            "contact": "cellular",
            "month": "may",
            "day_of_week": "mon",
            "poutcome": "nonexistent",
        }

        result = predict_single(pipeline, features_meta, input_data)
        total = result["probabilities"]["yes"] + result["probabilities"]["no"]
        assert abs(total - 1.0) < 1e-6

    def test_predict_different_inputs_different_results(self):
        """AC: 不同输入产生不同预测结果。"""
        pipeline, features_meta = load_model()
        assert pipeline is not None

        def _make_input(**overrides) -> dict:
            """创建默认输入并允许覆盖特定字段。"""
            base = {
                "age": 35,
                "duration": 180,
                "campaign": 1,
                "pdays": 999,
                "previous": 0,
                "emp_var_rate": 0.1,
                "cons_price_index": 93.0,
                "cons_conf_index": -40.0,
                "lending_rate3m": 2.0,
                "nr_employed": 5000.0,
                "job": "admin.",
                "marital": "single",
                "education": "high.school",
                "default": "no",
                "housing": "no",
                "loan": "no",
                "contact": "cellular",
                "month": "may",
                "day_of_week": "mon",
                "poutcome": "nonexistent",
            }
            base.update(overrides)
            return base

        # 高概率认购输入：长通话 + 之前成功
        high_risk = _make_input(duration=4000, poutcome="success")
        # 低概率认购输入：短通话 + 多次营销 + 之前失败
        low_risk = _make_input(duration=30, campaign=10, poutcome="failure")

        result_high = predict_single(pipeline, features_meta, high_risk)
        result_low = predict_single(pipeline, features_meta, low_risk)

        assert result_high["probabilities"]["yes"] != result_low["probabilities"]["yes"]

    def test_load_model_no_model_returns_none(self):
        """AC: 模型不存在时返回 (None, None)。"""

        saved_dir = PROJECT_ROOT / "model" / "saved_models"
        # 临时重命名模型目录
        temp_suffix = "_test_backup"
        renamed = False
        if (saved_dir / "model.joblib").exists():
            (saved_dir / "model.joblib").rename(
                saved_dir / f"model.joblib{temp_suffix}"
            )
            renamed = True

        try:
            pipeline, meta = load_model()
            assert pipeline is None
            assert meta is None
        finally:
            if renamed:
                (saved_dir / f"model.joblib{temp_suffix}").rename(
                    saved_dir / "model.joblib"
                )
