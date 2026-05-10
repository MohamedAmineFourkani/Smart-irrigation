"""
trainer.py
Trains Decision Tree, Random Forest, and XGBoost classifiers on
Soil_Moisture.csv, prints a comparison table, and saves .pkl files.
"""

import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

# Add project root to path so sibling imports work
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_fetcher import load_data, get_features_and_target, FEATURE_COLS

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

RANDOM_STATE = 42
TEST_SIZE    = 0.20


# ── Model definitions ─────────────────────────────────────────────────────────
def build_models() -> dict:
    return {
        "decision_tree": DecisionTreeClassifier(
            max_depth=8,
            min_samples_leaf=10,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_leaf=5,
            class_weight="balanced",
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
        "xgboost_model": XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            use_label_encoder=False,
            eval_metric="logloss",
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
    }


# ── Training & evaluation ────────────────────────────────────────────────────
def train_and_evaluate(verbose: bool = True) -> pd.DataFrame:
    """
    Full pipeline: load → split → train → evaluate → save.

    Returns
    -------
    pd.DataFrame  Summary metrics for all three models.
    """
    df = load_data()
    X, y = get_features_and_target(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )

    if verbose:
        print("=" * 60)
        print(" Smart Irrigation — Model Training")
        print("=" * 60)
        print(f"  Total samples : {len(df):,}")
        print(f"  Train / Test  : {len(X_train):,} / {len(X_test):,}")
        print(f"  Positive class: {y.sum():,} ({y.mean()*100:.1f} %)")
        print(f"  Features      : {FEATURE_COLS}")
        print()

    models  = build_models()
    records = []

    for name, model in models.items():
        # ── Cross-validation on training set ─────────────────────────────────
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
        cv_acc = cross_val_score(model, X_train, y_train, cv=cv,
                                 scoring="accuracy", n_jobs=-1).mean()

        # ── Final fit on full training set ────────────────────────────────────
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        acc  = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec  = recall_score(y_test, y_pred, zero_division=0)
        f1   = f1_score(y_test, y_pred, zero_division=0)

        records.append({
            "Model"          : name,
            "CV Accuracy"    : round(cv_acc, 4),
            "Test Accuracy"  : round(acc,    4),
            "Precision"      : round(prec,   4),
            "Recall"         : round(rec,    4),
            "F1 Score"       : round(f1,     4),
        })

        # ── Save model ────────────────────────────────────────────────────────
        out_path = MODELS_DIR / f"{name}.pkl"
        joblib.dump(model, out_path)

        if verbose:
            print(f"  [{name}]")
            print(f"    CV Accuracy : {cv_acc:.4f}")
            print(f"    Test Acc    : {acc:.4f}  Precision: {prec:.4f}"
                  f"  Recall: {rec:.4f}  F1: {f1:.4f}")
            print(f"    Saved  →  {out_path}")
            print()

    results = pd.DataFrame(records)

    if verbose:
        print("=" * 60)
        print(" Comparison Table")
        print("=" * 60)
        print(results.to_string(index=False))
        best = results.loc[results["F1 Score"].idxmax(), "Model"]
        print(f"\n  ✅  Best model by F1: [{best}]")
        print("=" * 60)

    return results


if __name__ == "__main__":
    train_and_evaluate()
