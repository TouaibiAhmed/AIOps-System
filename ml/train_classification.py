import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report

df = pd.read_csv("../data/processed_dataset.csv")
df_anomalies = df[df["label"] != "normal"]

feature_cols = [c for c in df.columns if c not in ["timestamp", "label"]]
X = df_anomalies[feature_cols]
y = df_anomalies["label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

clf = RandomForestClassifier(n_estimators=300, max_depth=10, random_state=42)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))

f1_macro = f1_score(y_test, y_pred, average="macro")
print(f"F1-score macro (classification) : {f1_macro:.3f}")

if f1_macro >= 0.85:
    joblib.dump(clf, "models/classifier.pkl")
    print("✅ Modèle de classification exporté.")
else:
    print("⚠️ F1-score insuffisant — vérifier l'équilibre des classes ou enrichir les features.")