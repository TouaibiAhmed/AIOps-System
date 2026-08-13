import pandas as pd

df = pd.read_csv("../data/processed_dataset.csv")

print("Répartition des labels (nombre) :")
print(df["label"].value_counts())
print()
print("Répartition des labels (%) :")
print(df["label"].value_counts(normalize=True) * 100)

print("Normal rows with cpu_usage > 0.5:", ((df["label"]=="normal") & (df["cpu_usage"]>0.5)).sum())
print("Normal rows with memory_usage > 0.3:", ((df["label"]=="normal") & (df["memory_usage"]>0.3)).sum())