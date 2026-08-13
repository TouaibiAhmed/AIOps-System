import requests
import pandas as pd
from datetime import datetime, timedelta, timezone

PROMETHEUS_URL = "http://localhost:9090"

QUERIES_CONTAINER = {
    "cpu_usage": 'sum(rate(container_cpu_usage_seconds_total{name="toy-app"}[30s])) * 100',
    "memory_usage": 'container_memory_usage_bytes{name="toy-app"} / (512*1024*1024) * 100',
    "network_receive": 'rate(container_network_receive_bytes_total{name="toy-app"}[30s])',
}



QUERIES = QUERIES_CONTAINER   


def query_range(query, start, end, step="15s"):
    resp = requests.get(f"{PROMETHEUS_URL}/api/v1/query_range", params={
        "query": query,
        "start": start.timestamp(),
        "end": end.timestamp(),
        "step": step,
    })
    resp.raise_for_status()
    return resp.json()["data"]["result"]


def to_dataframe(result, column_name):
    if not result:
        return pd.DataFrame(columns=["timestamp", column_name])
    values = result[0]["values"]
    df = pd.DataFrame(values, columns=["timestamp", column_name])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df[column_name] = df[column_name].astype(float)
    return df


def extract(hours_back=2):
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=hours_back)

    dfs = []
    for name, query in QUERIES.items():
        result = query_range(query, start, end)
        dfs.append(to_dataframe(result, name))

    merged = dfs[0]
    for df in dfs[1:]:
        merged = merged.merge(df, on="timestamp", how="outer")

    merged = merged.sort_values("timestamp").reset_index(drop=True)
    timestamp_str = end.strftime("%Y%m%d_%H%M%S")
    merged.to_csv(f"../data/metrics_{timestamp_str}.csv", index=False)
    print(f"Extraction terminée : {len(merged)} lignes sauvegardées.")
    print("\nTop 10 CPU values:")
    print(
    merged[["timestamp", "cpu_usage"]]
    .sort_values("cpu_usage", ascending=False)
    .head(10)
)
    return merged


if __name__ == "__main__":
    extract(hours_back=5)