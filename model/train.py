"""离线训练脚本 — 训练二分类模型并保存 Pipeline + 特征列表。"""

from __future__ import annotations

import json
import pathlib
import sys
import warnings

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore")

# 将项目根目录加入路径
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.data_loader import (  # noqa: E402
    CATEGORICAL_COLUMNS,
    FEATURE_COLUMNS,
    NUMERICAL_COLUMNS,
    TARGET_COLUMN,
    load_data,
)

SAVED_MODELS_DIR = PROJECT_ROOT / "model" / "saved_models"


def build_preprocessing_pipeline() -> ColumnTransformer:
    """构建预处理 Pipeline：分类字段 OHE + 数值字段标准化。"""
    cat_pipeline = OneHotEncoder(handle_unknown="ignore", sparse=False)
    num_pipeline = StandardScaler()

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_pipeline, NUMERICAL_COLUMNS),
            ("cat", cat_pipeline, CATEGORICAL_COLUMNS),
        ],
        remainder="drop",
    )
    return preprocessor


def train(
    test_size: float = 0.2,
    random_state: int = 42,
    n_estimators: int = 200,
    max_depth: int = 12,
) -> dict:
    """完整训练流程：加载→预处理→训练→评估→保存。"""
    print(">> Loading data...")
    df = load_data()
    print(f"   Loaded {len(df)} samples, {len(FEATURE_COLUMNS)} features")

    # 编码标签
    le = LabelEncoder()
    y = le.fit_transform(df[TARGET_COLUMN])  # no->0, yes->1
    X = df[FEATURE_COLUMNS]

    # 分割
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    print(f"   Train: {len(X_train)}, Test: {len(X_test)}")

    # 构建并训练 Pipeline
    preprocessor = build_preprocessing_pipeline()
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state,
        n_jobs=-1,
        class_weight="balanced",
    )

    print(">> Training RandomForest...")
    model.fit(preprocessor.fit_transform(X_train), y_train)
    print("   Training complete")

    # 评估
    y_pred = model.predict(preprocessor.transform(X_test))
    y_proba = model.predict_proba(preprocessor.transform(X_test))[:, 1]

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)

    print("\n>> Evaluation")
    print(f"   Accuracy: {acc:.4f}")
    print(f"   F1 Score: {f1:.4f}")
    print(f"   AUC:      {auc:.4f}")
    print(f"\n{classification_report(y_test, y_pred, target_names=['no', 'yes'])}")

    # 保存整个 Pipeline (preprocessor + model)
    from sklearn.pipeline import Pipeline

    full_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", model),
        ]
    )

    SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # 保存模型
    import joblib

    model_path = SAVED_MODELS_DIR / "model.joblib"
    joblib.dump(full_pipeline, model_path)
    print(f">> Model saved to {model_path}")

    # 保存特征列表
    features_meta = {
        "features": FEATURE_COLUMNS,
        "categorical": CATEGORICAL_COLUMNS,
        "numerical": NUMERICAL_COLUMNS,
        "target": TARGET_COLUMN,
        "class_names": ["no", "yes"],
        "training_samples": len(df),
        "auc": round(float(auc), 4),
        "f1": round(float(f1), 4),
        "accuracy": round(float(acc), 4),
    }
    features_path = SAVED_MODELS_DIR / "features.json"
    with open(features_path, "w") as f:
        json.dump(features_meta, f, indent=2)
    print(f">> Features metadata saved to {features_path}")

    # 特征重要性
    importances = model.feature_importances_
    # 获取 one-hot 编码后的特征名（兼容新旧 sklearn）
    cat_encoder = preprocessor.named_transformers_["cat"]
    if hasattr(cat_encoder, "get_feature_names_out"):
        cat_feature_names = cat_encoder.get_feature_names_out(CATEGORICAL_COLUMNS)
    else:
        cat_feature_names = cat_encoder.get_feature_names(CATEGORICAL_COLUMNS)
    all_feature_names = list(NUMERICAL_COLUMNS) + list(cat_feature_names)
    importance_df = pd.DataFrame(
        {"feature": all_feature_names, "importance": importances}
    ).sort_values("importance", ascending=False)

    importance_path = SAVED_MODELS_DIR / "feature_importance.csv"
    importance_df.to_csv(importance_path, index=False)
    print(f">> Feature importance saved to {importance_path}")
    print("\nTop 10 features:")
    print(importance_df.head(10).to_string(index=False))

    # 绘制 ROC 曲线并保存（兼容新旧 sklearn）
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.metrics import roc_curve

    fpr, tpr, _ = roc_curve(y_test, y_proba)
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, label=f"AUC = {auc:.4f}", linewidth=2)
    plt.plot([0, 1], [0, 1], "k--", alpha=0.5)
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend(loc="lower right")
    plt.grid(alpha=0.3)
    roc_path = SAVED_MODELS_DIR / "roc_curve.png"
    plt.savefig(roc_path, dpi=100, bbox_inches="tight")
    plt.close()
    print(f">> ROC curve saved to {roc_path}")

    return {
        "accuracy": acc,
        "f1": f1,
        "auc": auc,
        "model_path": str(model_path),
        "samples": len(df),
    }


if __name__ == "__main__":
    result = train()
    print(f"\n{'='*40}")
    print("Training completed successfully!")
    print(f"  AUC: {result['auc']:.4f}")
    print(f"  F1:  {result['f1']:.4f}")
    print(f"{'='*40}")
