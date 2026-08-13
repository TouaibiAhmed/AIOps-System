import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.metrics import f1_score, classification_report

df = pd.read_csv("../data/processed_dataset.csv")
feature_cols = [c for c in df.columns if c not in ["timestamp", "label"]]

# Entraînement uniquement sur les périodes "normal" (novelty detection)
df_healthy = df[df["label"] == "normal"]
model = IsolationForest(n_estimators=200, contamination="auto", random_state=42)
model.fit(df_healthy[feature_cols])

# Évaluation sur TOUT le dataset (normal + anomalies)
X_all = df[feature_cols]
df["anomaly_pred"] = model.predict(X_all)
df["anomaly_pred"] = df["anomaly_pred"].map({1: 0, -1: 1})
df["anomaly_true"] = (df["label"] != "normal").astype(int)

print(classification_report(df["anomaly_true"], df["anomaly_pred"]))
f1 = f1_score(df["anomaly_true"], df["anomaly_pred"])
print(f"F1-score détection : {f1:.3f}")

if f1 >= 0.85:
    joblib.dump(model, "models/isolation_forest.pkl")
    print("✅ Modèle de détection exporté.")
else:
    print("⚠️ F1-score sous le seuil (0.85) — revoir les features/données avant d'exporter.")