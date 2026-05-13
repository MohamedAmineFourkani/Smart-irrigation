"""
cluster_trainer.py
─────────────────────────────────────────────────────────────────────────────
Trains KMeans + Random Forest cluster classifier on NASA POWER historical data.
Reads data/data.csv → saves nasa_scaler.pkl, nasa_kmeans.pkl, nasa_rf_cluster.pkl
"""

import sys
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier

SRC_DIR = Path(__file__).resolve().parent
DATA_DIR = SRC_DIR.parent / "data"
MODELS_DIR = SRC_DIR.parent / "models"

FEATURES = ["temp", "humidity", "wind", "rain", "solar_rad", "pressure"]

CLUSTER_LABELS = {
    0: "VERY_DRY",
    1: "DRY",
    2: "MILD",
    3: "WET",
    4: "VERY_WET",
}


def _n_clusters() -> int:
    return len(CLUSTER_LABELS)


def _remap_to_consistent(kmeans, X_scaled, rain_idx):
    """Remap KMeans arbitrary cluster IDs to 0..n-1 by ascending rain."""
    centers = kmeans.cluster_centers_
    rain_centers = centers[:, rain_idx]
    order = np.argsort(rain_centers)
    return {order[i]: i for i in range(len(order))}


def _print_characteristics(df_with_cluster):
    """Print mean ± std for each feature per cluster."""
    print("\n" + "=" * 72)
    print("  Cluster Characteristics Table (mean ± std)")
    print("=" * 72)
    header = f"{'Cluster':<10s}" + "".join(f"{f:>13s}" for f in FEATURES)
    print(header)
    print("-" * len(header))
    for c in sorted(df_with_cluster["cluster"].unique()):
        subset = df_with_cluster[df_with_cluster["cluster"] == c]
        label = CLUSTER_LABELS.get(c, f"Cluster {c}")
        row = f"{label:<10s}"
        for feat in FEATURES:
            row += f"{subset[feat].mean():>7.2f} ±{subset[feat].std():>5.2f}"
        print(row)
    print("=" * 72)


def train(verbose=True):
    """
    Load data.csv, train KMeans + RF, save 3 models to models/.
    Returns True on success.
    """
    csv_path = DATA_DIR / "data.csv"
    if not csv_path.exists():
        print(f"  ❌  data.csv not found at {csv_path}")
        return False

    if verbose:
        print(f"\n  📊  Loading {csv_path}...")

    df = pd.read_csv(csv_path, index_col=0)
    X = df[FEATURES].dropna()

    if verbose:
        print(f"  Rows: {len(X)}  |  Features: {len(FEATURES)}")

    # ── Scale ────────────────────────────────────────────────────────────────
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ── KMeans ───────────────────────────────────────────────────────────────
    kmeans = KMeans(n_clusters=_n_clusters(), random_state=42, n_init=10)
    clusters_raw = kmeans.fit_predict(X_scaled)

    # ── Remap to consistent 0=DRY, 1=MILD, 2=WET by ascending rain ──────────
    rain_idx = FEATURES.index("rain")
    remap = _remap_to_consistent(kmeans, X_scaled, rain_idx)
    y = np.array([remap[c] for c in clusters_raw])

    # ── RF classifier ────────────────────────────────────────────────────────
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_scaled, y)

    # ── Save ─────────────────────────────────────────────────────────────────
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, MODELS_DIR / "nasa_scaler.pkl")
    joblib.dump(kmeans, MODELS_DIR / "nasa_kmeans.pkl")
    joblib.dump(rf, MODELS_DIR / "nasa_rf_cluster.pkl")

    if verbose:
        print(f"  💾  Saved:")
        print(f"       → {MODELS_DIR / 'nasa_scaler.pkl'}")
        print(f"       → {MODELS_DIR / 'nasa_kmeans.pkl'}")
        print(f"       → {MODELS_DIR / 'nasa_rf_cluster.pkl'}")

    # ── Cluster characteristics ──────────────────────────────────────────────
    df_clustered = X.copy()
    df_clustered["cluster"] = y
    _print_characteristics(df_clustered)

    # ── Label mapping ────────────────────────────────────────────────────────
    if verbose:
        print(f"\n  Cluster mapping (by ascending rain):")
        for k, v in CLUSTER_LABELS.items():
            print(f"    {k} → {v}")

    return True


if __name__ == "__main__":
    train()
