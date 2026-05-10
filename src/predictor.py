"""
predictor.py
Generic prediction interface — loads any of the three saved models and
returns a prediction for a single sensor reading or a batch DataFrame.
"""

import sys
from pathlib import Path
from typing import Literal, Union

import joblib
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_fetcher import FEATURE_COLS

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

ModelType = Literal["decision_tree", "random_forest", "xgboost_model"]

# ── In-process model cache (avoids re-loading from disk on every call) ────────
_MODEL_CACHE: dict = {}


def _load_model(model_type: ModelType):
    """Load model from disk (cached after first load)."""
    if model_type not in _MODEL_CACHE:
        model_path = MODELS_DIR / f"{model_type}.pkl"
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {model_path}\n"
                "Run trainer.py first to generate the .pkl files."
            )
        _MODEL_CACHE[model_type] = joblib.load(model_path)
    return _MODEL_CACHE[model_type]


def predict(
    data: Union[pd.DataFrame, dict],
    model_type: ModelType = "random_forest",
) -> np.ndarray:
    """
    Predict irrigation requirement for one or more sensor readings.

    Parameters
    ----------
    data       : dict with keys matching FEATURE_COLS, or a DataFrame.
    model_type : One of "decision_tree", "random_forest", "xgboost_model".

    Returns
    -------
    np.ndarray of int (0 = no irrigation, 1 = irrigation required).
    """
    model = _load_model(model_type)

    if isinstance(data, dict):
        X = pd.DataFrame([data])[FEATURE_COLS]
    else:
        X = data[FEATURE_COLS].copy()

    return model.predict(X)


def predict_proba(
    data: Union[pd.DataFrame, dict],
    model_type: ModelType = "random_forest",
) -> np.ndarray:
    """
    Return class probabilities [P(0), P(1)] for each sample.
    """
    model = _load_model(model_type)

    if isinstance(data, dict):
        X = pd.DataFrame([data])[FEATURE_COLS]
    else:
        X = data[FEATURE_COLS].copy()

    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)
    else:
        preds = model.predict(X)
        return np.column_stack([1 - preds, preds]).astype(float)


def clear_cache():
    """Force model reload on the next predict call (useful for testing)."""
    _MODEL_CACHE.clear()


if __name__ == "__main__":
    sample = {"temp_SOIL": 14.5, "water_SOIL": 12.0, "conduct_SOIL": 145}
    for mt in ("decision_tree", "random_forest", "xgboost_model"):
        pred  = predict(sample, model_type=mt)[0]
        proba = predict_proba(sample, model_type=mt)[0]
        print(f"[{mt}] prediction={pred}  P(irrigation)={proba[1]:.3f}")
