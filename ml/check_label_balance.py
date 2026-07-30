import pandas as pd

df = pd.read_csv("../data/processed_dataset.csv")

print("Répartition des labels (nombre) :")
print(df["label"].value_counts())
print()
print("Répartition des labels (%) :")
print(df["label"].value_counts(normalize=True) * 100)