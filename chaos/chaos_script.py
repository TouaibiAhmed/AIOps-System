import requests
import random
import time
import csv
from datetime import datetime, timezone

TOY_APP_URL = "http://localhost:8000"
LOG_FILE = "../data/chaos_labels.csv"
COOLDOWN_SECONDS = 20


def build_balanced_schedule(n_per_class=50):
    schedule = (
        ["cpu"] * n_per_class
        + ["memory"] * n_per_class
        + ["network"] * n_per_class
        + ["normal"] * n_per_class
    )
    random.shuffle(schedule)
    return schedule


def trigger_incident(incident_type):
    """Retourne la durée réelle de l'incident, pour que le script sache
    combien de temps attendre avant de fermer la fenêtre labellisée."""
    if incident_type == "cpu":
        duration = random.randint(20, 45)
        requests.get(f"{TOY_APP_URL}/stress-cpu", params={"duration": duration})
        return duration   # NOUVEAU : on retourne la vraie durée choisie

    elif incident_type == "memory":
        size = random.randint(120, 300)
        requests.get(f"{TOY_APP_URL}/leak-memory", params={"size_mb": size})
        return 20   # allocation quasi instantanée, pas besoin d'attendre longtemps

    elif incident_type == "network":
        requests_count = random.randint(500, 1500)
        start = time.time()
        requests.get(
         f"{TOY_APP_URL}/network-spike",
         params={"requests_count": requests_count}
        )
        duration = time.time() - start
        return duration


    return 30   # "normal" : valeur par défaut, non utilisée


def log_event(incident_type, start, end):
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([start, end, incident_type])


def run_chaos_loop(n_per_class=40):
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
            real_duration = trigger_incident(incident_type)
        except Exception as e:
            print(f"Incident failed: {e}")
            real_duration = 30

        # NOUVEAU : on attend la VRAIE durée + une marge de sécurité,
        # au lieu d'un sleep(30) fixe déconnecté du paramètre envoyé
        wait_time = real_duration + 5 if incident_type != "normal" else 30
        time.sleep(wait_time)

        end = datetime.now(timezone.utc).isoformat()
        log_event(incident_type, start, end)

        requests.get(f"{TOY_APP_URL}/reset-memory")

        time.sleep(COOLDOWN_SECONDS)
        

    print("Chaos loop terminée.")


if __name__ == "__main__":
    run_chaos_loop(n_per_class=40)   # validation d'abord