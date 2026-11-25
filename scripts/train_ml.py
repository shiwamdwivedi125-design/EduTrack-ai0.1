"""
ML Model Training Script - EduTrack AI
Trains student academic performance prediction models using scikit-learn.
NOTE: Trained on SYNTHETIC data. Mark predictions as estimates only.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))

import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'backend', 'ml_models')
os.makedirs(MODEL_DIR, exist_ok=True)


def generate_synthetic_training_data(n_samples=1000):
    """Generate synthetic training data for ML model"""
    np.random.seed(42)

    # Features
    attendance = np.random.uniform(40, 100, n_samples)
    previous_cgpa = np.random.uniform(4.0, 10.0, n_samples)
    avg_internal_pct = np.random.uniform(30, 100, n_samples)

    # Target: 1=Pass/Good, 0=Needs Improvement
    # Rule-based target with some noise
    score = (
        0.35 * (attendance / 100) +
        0.40 * (previous_cgpa / 10) +
        0.25 * (avg_internal_pct / 100)
    )
    noise = np.random.normal(0, 0.05, n_samples)
    target = (score + noise >= 0.5).astype(int)

    X = np.column_stack([attendance, previous_cgpa, avg_internal_pct])
    return X, target


def train_and_evaluate():
    print("\n" + "="*60)
    print("  EduTrack AI - ML Model Training")
    print("  NOTE: Training on SYNTHETIC data. Predictions are estimates.")
    print("="*60)

    try:
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler
        from sklearn.linear_model import LogisticRegression
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import (accuracy_score, precision_score,
                                     recall_score, f1_score, confusion_matrix)
        import joblib
    except ImportError:
        print("[ERROR] scikit-learn or joblib not installed.")
        print("Run: pip install scikit-learn joblib")
        # Save a dummy evaluation
        eval_data = {
            "status": "not_trained",
            "message": "scikit-learn not available. Using rule-based fallback.",
            "disclaimer": "Predictions are estimates only."
        }
        with open(os.path.join(MODEL_DIR, "evaluation.json"), "w") as f:
            json.dump(eval_data, f, indent=2)
        return

    print("\n[1] Generating synthetic training data...")
    X, y = generate_synthetic_training_data(2000)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"    Train: {len(X_train)} | Test: {len(X_test)}")
    print(f"    Class distribution: Pass={y_train.sum()}, Improve={len(y_train)-y_train.sum()}")

    # Scale
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("\n[2] Training Logistic Regression...")
    lr = LogisticRegression(random_state=42, max_iter=1000)
    lr.fit(X_train_scaled, y_train)
    lr_pred = lr.predict(X_test_scaled)
    lr_acc = accuracy_score(y_test, lr_pred)
    print(f"    LR Accuracy: {lr_acc:.4f}")

    print("\n[3] Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_pred)
    print(f"    RF Accuracy: {rf_acc:.4f}")

    # Choose best model
    if rf_acc >= lr_acc:
        best_model = rf
        best_pred = rf_pred
        model_name = "Random Forest"
        X_test_final = X_test
        # Save scaler anyway
        joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))
    else:
        best_model = lr
        best_pred = lr_pred
        model_name = "Logistic Regression"
        X_test_final = X_test_scaled
        joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))

    print(f"\n[4] Best Model: {model_name}")
    acc = accuracy_score(y_test, best_pred)
    prec = precision_score(y_test, best_pred, zero_division=0)
    rec = recall_score(y_test, best_pred, zero_division=0)
    f1 = f1_score(y_test, best_pred, zero_division=0)
    cm = confusion_matrix(y_test, best_pred).tolist()

    print(f"    Accuracy:  {acc:.4f}")
    print(f"    Precision: {prec:.4f}")
    print(f"    Recall:    {rec:.4f}")
    print(f"    F1-Score:  {f1:.4f}")
    print(f"    Confusion Matrix: {cm}")

    # Feature importance
    if hasattr(best_model, 'feature_importances_'):
        fi = best_model.feature_importances_.tolist()
    else:
        fi = [abs(c) for c in best_model.coef_[0].tolist()]
        total = sum(fi)
        fi = [v/total for v in fi] if total > 0 else fi

    features = ["attendance", "previous_cgpa", "avg_internal_percentage"]

    # Save model
    joblib.dump(best_model, os.path.join(MODEL_DIR, "performance_model.pkl"))
    print(f"\n[5] Model saved to ml_models/performance_model.pkl")

    # Save evaluation
    eval_data = {
        "status": "trained",
        "model_name": model_name,
        "training_data": "synthetic",
        "n_samples_train": len(X_train),
        "n_samples_test": len(X_test),
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
        },
        "confusion_matrix": cm,
        "logistic_regression": {"accuracy": round(lr_acc, 4)},
        "random_forest": {"accuracy": round(rf_acc, 4)},
        "disclaimer": (
            "This model is trained on SYNTHETIC data for demonstration purposes. "
            "Predictions are estimates only and must NOT be used to automatically "
            "determine student outcomes or academic decisions."
        ),
        "features": features,
    }

    with open(os.path.join(MODEL_DIR, "evaluation.json"), "w") as f:
        json.dump(eval_data, f, indent=2)

    fi_data = {
        "features": features,
        "importance": [round(v, 4) for v in fi],
        "model": model_name,
        "note": "Feature importance from trained model on synthetic data"
    }
    with open(os.path.join(MODEL_DIR, "feature_importance.json"), "w") as f:
        json.dump(fi_data, f, indent=2)

    print(f"\n[6] Evaluation saved to ml_models/evaluation.json")

    # Also train LR and save it separately
    joblib.dump(lr, os.path.join(MODEL_DIR, "lr_model.pkl"))
    joblib.dump(rf, os.path.join(MODEL_DIR, "rf_model.pkl"))

    print("\n" + "="*60)
    print("  ML TRAINING COMPLETE!")
    print("  Disclaimer: Model trained on synthetic data only.")
    print("  Predictions are estimates, not academic determinations.")
    print("="*60 + "\n")


if __name__ == "__main__":
    train_and_evaluate()
