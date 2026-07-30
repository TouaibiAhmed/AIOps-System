import requests
import random
import time
import csv
from datetime import datetime, timezone

TOY_APP_URL = "http://localhost:8000"
LOG_FILE = "../data/chaos_labels.csv"


def build_balanced_schedule(n_per_class=50):
    """Planning équilibré (nombre égal de chaque type), puis mélangé pour éviter
    tout biais temporel (warmup système, dérive thermique, heure de la journée)."""
    schedule = (
        ["cpu"] * n_per_class
        + ["memory"] * n_per_class
        + ["network"] * n_per_class
        + ["normal"] * n_per_class
    )
    random.shuffle(schedule)
    return schedule


def trigger_incident(incident_type):

    if incident_type == "cpu":
        duration = random.randint(20, 45)
        requests.get(
    f"{TOY_APP_URL}/stress-cpu",
    params={"duration": duration}
)
        
    elif incident_type == "memory":
        size = random.randint(120, 300)

        requests.get(
        f"{TOY_APP_URL}/leak-memory",
        params={"size_mb": size}
    )
    elif incident_type == "network":
        requests_count = random.randint(500, 1500)

        requests.get(
        f"{TOY_APP_URL}/network-spike",
        params={"requests_count": requests_count}
    )
    # "normal" = on ne fait rien


def log_event(incident_type, start, end):
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([start, end, incident_type])


def run_chaos_loop(n_per_class=50):
    schedule = build_balanced_schedule(n_per_class)
    total_cycles = len(schedule)

    counts = {t: schedule.count(t) for t in set(schedule)}
    print(f"Planning généré : {total_cycles} cycles -> {counts}")

    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["start_time", "end_time", "incident_type"])

    for i, incident_type in enumerate(schedule):
        start = datetime.now(timezone.utc).isoformat()
        print(f"[{i + 1}/{total_cycles}] Déclenchement : {incident_type}")

        try:
         trigger_incident(incident_type)
        except Exception as e:
         print(f"Incident failed: {e}")
        time.sleep(30)

        end = datetime.now(timezone.utc).isoformat()
        log_event(incident_type, start, end)

        requests.get(f"{TOY_APP_URL}/reset-memory")
        time.sleep(random.randint(8, 20))
    print("Chaos loop terminée.")


if __name__ == "__main__":
    run_chaos_loop(n_per_class=50)   # VALIDATION : petit run d'abord (~13 min)
    # Une fois confirmé -> repasser à n_per_class=50 (~2h20) pour le dataset final