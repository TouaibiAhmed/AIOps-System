"""
run_pipeline.py — Orchestrateur du pipeline AIOps

Lance automatiquement, dans l'ordre :
  1. chaos_script.py         (peut durer plusieurs heures)
  2. Attente tampon           (laisse Prometheus scraper les dernières métriques)
  3. extract_prometheus.py    (extraction du CSV brut)
  4. preprocessing.py         (nettoyage, labeling, dataset final)

Place ce fichier à la RACINE de ton projet (aiops-project/), au même niveau
que les dossiers chaos/, etl/, ml/, data/.

Utilisation :
    python run_pipeline.py                      # utilise les valeurs par défaut
    python run_pipeline.py --n-per-class 50      # change le nombre de cycles
    python run_pipeline.py --post-wait 90        # change le buffer d'attente (secondes)
"""

import subprocess
import time
import sys
import os
import re
import glob
import argparse
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CHAOS_DIR = os.path.join(PROJECT_ROOT, "chaos")
ETL_DIR = os.path.join(PROJECT_ROOT, "etl")
ML_DIR = os.path.join(PROJECT_ROOT, "ml")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")


def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")


def run_step(script_name, cwd):
    """Exécute un script Python et arrête tout le pipeline s'il échoue."""
    cmd = [sys.executable, script_name]
    log(f"{'=' * 60}")
    log(f">>> Lancement : {script_name}  (dossier : {cwd})")
    log(f"{'=' * 60}")

    result = subprocess.run(cmd, cwd=cwd)

    if result.returncode != 0:
        log(f"❌ {script_name} a échoué (code de sortie {result.returncode}).")
        log("Pipeline arrêté — corrige l'erreur ci-dessus avant de relancer.")
        sys.exit(1)

    log(f"✅ {script_name} terminé avec succès.\n")


def update_chaos_n_per_class(n):
    """Modifie automatiquement la valeur n_per_class dans chaos_script.py."""
    chaos_path = os.path.join(CHAOS_DIR, "chaos_script.py")
    with open(chaos_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_content, count = re.subn(
        r"run_chaos_loop\(n_per_class=\d+\)",
        f"run_chaos_loop(n_per_class={n})",
        content,
    )

    if count == 0:
        log(f"⚠️ Impossible de trouver 'run_chaos_loop(n_per_class=...)' dans "
            f"{chaos_path} — vérifie manuellement que n_per_class={n} est bien défini.")
        return

    with open(chaos_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    log(f"📝 chaos_script.py mis à jour -> n_per_class={n}")


def get_latest_metrics_file():
    """Trouve le fichier metrics_*.csv le plus récent dans data/."""
    files = glob.glob(os.path.join(DATA_DIR, "metrics_*.csv"))
    if not files:
        raise FileNotFoundError(
            "Aucun fichier metrics_*.csv trouvé dans data/. "
            "L'extraction a-t-elle bien fonctionné ?"
        )
    return max(files, key=os.path.getmtime)


def update_preprocessing_metrics_file(new_path):
    """Met à jour automatiquement METRICS_FILE dans preprocessing.py
    pour qu'il pointe vers le fichier fraîchement extrait."""
    preprocessing_path = os.path.join(ML_DIR, "preprocessing.py")
    with open(preprocessing_path, "r", encoding="utf-8") as f:
        content = f.read()

    rel_path = "../data/" + os.path.basename(new_path)
    new_content, count = re.subn(
        r'METRICS_FILE\s*=\s*".*?"',
        f'METRICS_FILE = "{rel_path}"',
        content,
    )

    if count == 0:
        log(f"⚠️ Impossible de trouver 'METRICS_FILE = \"...\"' dans "
            f"{preprocessing_path} — mets à jour manuellement avec : {rel_path}")
        return

    with open(preprocessing_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    log(f"📝 preprocessing.py mis à jour -> METRICS_FILE = \"{rel_path}\"")


def main():
    parser = argparse.ArgumentParser(description="Pipeline AIOps automatisé.")
    parser.add_argument(
        "--n-per-class", type=int, default=40,
        help="Nombre de cycles par type d'incident (défaut: 40, ≈ 3h20)."
    )
    parser.add_argument(
        "--post-wait", type=int, default=60,
        help="Secondes d'attente après le chaos script avant l'extraction "
             "(défaut: 60s, laisse Prometheus scraper les dernières métriques)."
    )
    parser.add_argument(
        "--skip-chaos", action="store_true",
        help="Ignore l'étape du chaos script (utile si tu as déjà des données "
             "et veux juste relancer extraction + preprocessing)."
    )
    args = parser.parse_args()

    pipeline_start = datetime.now()
    log(f"🚀 Pipeline AIOps démarré — n_per_class={args.n_per_class}, "
        f"post_wait={args.post_wait}s")

    # Étape 1 : Chaos Script
    if not args.skip_chaos:
        update_chaos_n_per_class(args.n_per_class)
        run_step("chaos_script.py", CHAOS_DIR)

        # Étape 2 : Attente tampon avant extraction
        log(f"⏳ Attente de {args.post_wait}s pour laisser Prometheus "
            f"finir de scraper les dernières métriques...")
        time.sleep(args.post_wait)
    else:
        log("⏭️  Étape chaos ignorée (--skip-chaos).")

    # Étape 3 : Extraction ETL
    run_step("extract_prometheus.py", ETL_DIR)

    # Étape 4 : Mise à jour du nom de fichier + Preprocessing
    latest_file = get_latest_metrics_file()
    log(f"📄 Dernier fichier extrait détecté : {os.path.basename(latest_file)}")
    update_preprocessing_metrics_file(latest_file)
    run_step("preprocessing.py", ML_DIR)

    pipeline_end = datetime.now()
    duration = pipeline_end - pipeline_start
    log(f"🎉 Pipeline complet terminé ! Durée totale : {duration}")
    log("Vérifie maintenant les résultats du 'LABEL QUALITY CHECK' ci-dessus "
        "avant de passer à l'entraînement des modèles.")


if __name__ == "__main__":
    main()