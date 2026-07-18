import requests
import random
import time
import csv
from datetime import datetime, timezone

TOY_APP_URL = "http://localhost:8000"
LOG_FILE = "../data/chaos_labels.csv"

INCIDENT_TYPES = ["cpu", "memory", "network", "normal"]

def trigger_incident(incident_type):
    if incident_type == "cpu":
        requests.get(f"{TOY_APP_URL}/stress-cpu", params={"duration": 30})
    elif incident_type == "memory":
        requests.get(f"{TOY_APP_URL}/leak-memory", params={"size_mb": 200})
    elif incident_type == "network":
        requests.get(f"{TOY_APP_URL}/network-spike")
    # "normal" = on ne fait rien, période de calme

def log_event(incident_type, start, end):
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([start, end, incident_type])

def run_chaos_loop(cycles=20):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["start_time", "end_time", "incident_type"])

    for i in range(cycles):
        incident_type = random.choice(INCIDENT_TYPES)
        start = datetime.now(timezone.utc).isoformat()
        print(f"[{i+1}/{cycles}] Déclenchement : {incident_type}")

        trigger_incident(incident_type)
        time.sleep(30)   # laisse le temps à l'incident de produire un effet mesurable

        end = datetime.now(timezone.utc).isoformat()
        log_event(incident_type, start, end)

        requests.get(f"{TOY_APP_URL}/reset-memory")   # nettoyage avant le prochain cycle
        time.sleep(10)   # période de repos entre deux incidents

if __name__ == "__main__":
    run_chaos_loop(cycles=20)