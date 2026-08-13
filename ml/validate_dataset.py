import pandas as pd

RAW_METRICS = "../data/metrics_20260810_161541.csv"
PROCESSED_DATASET = "../data/processed_dataset2.csv"


# ============================================================
# 1. VALIDATE RAW METRICS + LABELS
# ============================================================

df = pd.read_csv(RAW_METRICS)

print("\n==============================")
print("RAW DATASET QUALITY")
print("==============================")

print("\nDataset shape:")
print(df.shape)

print("\nMissing values:")
print(df.isna().sum())


# ------------------------------------------------------------
# Class distribution
# ------------------------------------------------------------

print("\nClass counts:")
print(df["label"].value_counts())


# ------------------------------------------------------------
# Normal contamination
# ------------------------------------------------------------

normal_cpu = (
    (df["label"] == "normal") &
    (df["cpu_usage"] > 20)
).sum()

normal_memory = (
    (df["label"] == "normal") &
    (df["memory_usage"] > 25)
).sum()

normal_network = (
    (df["label"] == "normal") &
    (df["network_receive"] > 500)
).sum()


print("\nNormal contamination:")
print("Normal + CPU > 20%:", normal_cpu)
print("Normal + Memory > 25%:", normal_memory)
print("Normal + Network > 500:", normal_network)


# ------------------------------------------------------------
# Incident quality
# ------------------------------------------------------------

cpu_bad = (
    (df["label"] == "cpu") &
    (df["cpu_usage"] < 20)
).sum()

memory_bad = (
    (df["label"] == "memory") &
    (df["memory_usage"] < 25)
).sum()

network_bad = (
    (df["label"] == "network") &
    (df["network_receive"] < 500)
).sum()


print("\nIncident quality:")
print("CPU + CPU < 20%:", cpu_bad)
print("Memory + Memory < 25%:", memory_bad)
print("Network + Network < 500:", network_bad)


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

print("\n==============================")
print("QUALITY SUMMARY")
print("==============================")

if (
    normal_cpu == 0
    and normal_memory == 0
    and normal_network == 0
    and cpu_bad == 0
    and memory_bad == 0
    and network_bad == 0
):
    print("PASS: Dataset quality looks good.")
else:
    print("FAIL: Dataset contains suspicious labels/signals.")