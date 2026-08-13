import pandas as pd
import numpy as np


def load_and_clean(csv_path):
    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    if df["timestamp"].dt.tz is not None:
        df["timestamp"] = df["timestamp"].dt.tz_localize(None)

   
    df = df.interpolate(method="linear", limit=2)
    df = df.dropna()

    return df


def label_from_chaos(df, chaos_csv_path):

    chaos = pd.read_csv(
        chaos_csv_path,
        parse_dates=[
            "start_time",
            "end_time"
        ]
    )

    # Make chaos timestamps timezone-naive
    chaos["start_time"] = (
        chaos["start_time"]
        .dt
        .tz_localize(None)
    )

    chaos["end_time"] = (
        chaos["end_time"]
        .dt
        .tz_localize(None)
    )

    chaos = (
        chaos
        .sort_values("start_time")
        .reset_index(drop=True)
    )

    df = (
        df
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    df["label"] = None

    # Explicit interval labeling
    for _, row in chaos.iterrows():

        mask = (
            (df["timestamp"] >= row["start_time"]) &
            (df["timestamp"] <= row["end_time"])
        )

        df.loc[
            mask,
            "label"
        ] = row["incident_type"]

    # Remove metric rows that don't belong
    # to an explicitly labeled interval.
    df = df.dropna(
        subset=["label"]
    )

    return df.reset_index(drop=True)


def add_rolling_features(df, window=3):

    df = (
        df
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    # Detect gaps between Prometheus observations
    gap = (
        df["timestamp"]
        .diff()
        .dt
        .total_seconds()
    )

    # Start a new block when:
    # 1. label changes
    # 2. there is a timestamp gap
    df["block_id"] = (
        (
            df["label"] !=
            df["label"].shift(1)
        )
        |
        (gap > 15.5)
    ).cumsum()

    numeric_cols = [
        c
        for c in df.select_dtypes(
            include=[np.number]
        ).columns
        if c != "block_id"
    ]

    for col in numeric_cols:

        grp = df.groupby(
            "block_id"
        )[col]

        df[
            f"{col}_rolling_mean"
        ] = grp.transform(
            lambda s:
            s.rolling(
                window,
                min_periods=1
            ).mean()
        )

        df[
            f"{col}_rolling_std"
        ] = grp.transform(
            lambda s:
            s.rolling(
                window,
                min_periods=1
            ).std()
            .fillna(0)
        )

    return df.drop(
        columns=["block_id"]
    )


def normalize(
    df,
    exclude=["timestamp", "label"]
):

    cols = [
        c
        for c in df.columns
        if c not in exclude
    ]

    for col in cols:

        min_val = df[col].min()
        max_val = df[col].max()

        if max_val > min_val:

            df[col] = (
                df[col] - min_val
            ) / (
                max_val - min_val
            )

    return df


if __name__ == "__main__":

    # CHANGE THIS AFTER EACH NEW EXTRACTION
    METRICS_FILE = "../data/metrics_20260812_014827.csv"

    CHAOS_FILE = "../data/chaos_labels.csv"

    OUTPUT_FILE = "../data/processed_dataset.csv"


    # =========================================================
    # 1. LOAD
    # =========================================================

    df = load_and_clean(
        METRICS_FILE
    )

    print(
        f"Raw metric rows: {len(df)}"
    )


    # =========================================================
    # 2. LABEL
    # =========================================================

    df = label_from_chaos(
        df,
        CHAOS_FILE
    )

    print(
        f"Labeled rows: {len(df)}"
    )


    # =========================================================
    # 3. LABEL QUALITY
    # =========================================================

    print(
        "\n===== LABEL QUALITY CHECK ====="
    )

    print(
        "\nClass counts:"
    )

    print(
        df["label"].value_counts()
    )


    # Normal contamination

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


    print(
        "\nNormal + CPU > 20:",
        normal_cpu
    )

    print(
        "Normal + Memory > 25:",
        normal_memory
    )

    print(
        "Normal + Network > 500:",
        normal_network
    )


    # Incident weak rows

    cpu_bad = (
        (df["label"] == "cpu") &
        (df["cpu_usage"] < 20)
    ).sum()

    cpu_total = (
        df["label"] == "cpu"
    ).sum()

    memory_bad = (
        (df["label"] == "memory") &
        (df["memory_usage"] < 25)
    ).sum()

    memory_total = (
        df["label"] == "memory"
    ).sum()

    network_bad = (
        (df["label"] == "network") &
        (df["network_receive"] < 500)
    ).sum()

    network_total = (
        df["label"] == "network"
    ).sum()


    print(
        "\n===== INCIDENT QUALITY ====="
    )

    if cpu_total > 0:
        print(
            f"CPU weak rows: "
            f"{cpu_bad}/{cpu_total} "
            f"({cpu_bad / cpu_total * 100:.1f}%)"
        )

    if memory_total > 0:
        print(
            f"Memory weak rows: "
            f"{memory_bad}/{memory_total} "
            f"({memory_bad / memory_total * 100:.1f}%)"
        )

    if network_total > 0:
        print(
            f"Network weak rows: "
            f"{network_bad}/{network_total} "
            f"({network_bad / network_total * 100:.1f}%)"
        )


    # =========================================================
    # 4. ROLLING FEATURES
    # =========================================================

    df = add_rolling_features(
        df,
        window=3
    )


    # =========================================================
    # 5. NORMALIZATION
    # =========================================================

    df = normalize(
        df
    )


    # =========================================================
    # 6. SAVE
    # =========================================================

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        "\nDataset final prêt:",
        df.shape
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )