"""在线预测模块 — 加载训练好的模型 Pipeline，对新样本进行预测。"""

from __future__ import annotations

import json
import pathlib
import sys
from typing import Any

import pandas as pd

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


SAVED_MODELS_DIR = PROJECT_ROOT / "model" / "saved_models"


def load_model():
    """加载保存的模型 Pipeline 和特征元数据。

    Returns:
        (pipeline, features_meta) 或 (None, None) 如果模型不存在。
    """
    import joblib

    model_path = SAVED_MODELS_DIR / "model.joblib"
    features_path = SAVED_MODELS_DIR / "features.json"

    if not model_path.exists() or not features_path.exists():
        return None, None

    pipeline = joblib.load(model_path)
    with open(features_path) as f:
        features_meta = json.load(f)

    return pipeline, features_meta


def predict_single(pipeline, features_meta: dict, input_data: dict[str, Any]) -> dict:
    """对单条输入进行预测。

    Args:
        pipeline: 训练好的完整 Pipeline(preprocessor + classifier)
        features_meta: 特征元数据
        input_data: 用户输入的字段值字典

    Returns:
        预测结果字典，含类别、概率、置信度等级。
    """
    # 构建 DataFrame (确保列顺序与训练一致)
    row = {col: input_data.get(col, "") for col in features_meta["features"]}
    df = pd.DataFrame([row])

    # 预测
    y_pred = pipeline.predict(df)[0]
    y_proba = pipeline.predict_proba(df)[0]

    predicted_class = features_meta["class_names"][int(y_pred)]
    probability = float(y_proba[int(y_pred)])

    # 置信度等级
    if probability >= 0.9:
        confidence = "高置信度"
    elif probability >= 0.7:
        confidence = "中置信度"
    else:
        confidence = "低置信度"

    return {
        "prediction": predicted_class,
        "probability": probability,
        "confidence": confidence,
        "probabilities": {
            features_meta["class_names"][0]: float(y_proba[0]),
            features_meta["class_names"][1]: float(y_proba[1]),
        },
    }
