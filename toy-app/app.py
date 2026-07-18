from fastapi import FastAPI
import threading
import time

app = FastAPI()

# Variable globale pour simuler une fuite mémoire
memory_leak_list = []

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/stress-cpu")
def stress_cpu(duration: int = 20):
    """Sature un coeur CPU pendant `duration` secondes."""
    def burn():
        end_time = time.time() + duration
        while time.time() < end_time:
            _ = 999999 ** 2   # calcul inutile mais coûteux en CPU
    threading.Thread(target=burn).start()
    return {"action": "cpu_stress_started", "duration": duration}

@app.get("/leak-memory")
def leak_memory(size_mb: int = 100):
    """Alloue de la mémoire sans jamais la libérer."""
    global memory_leak_list
    memory_leak_list.append(bytearray(size_mb * 1024 * 1024))
    return {"action": "memory_leaked", "total_chunks": len(memory_leak_list)}

@app.get("/reset-memory")
def reset_memory():
    global memory_leak_list
    memory_leak_list = []
    return {"action": "memory_reset"}

@app.get("/network-spike")
def network_spike():
    """Simule un pic réseau (ici juste un placeholder, à enrichir si besoin)."""
    import requests
    for _ in range(50):
        try:
            requests.get("https://pypi.org", timeout=1)
        except Exception:
            pass
    return {"action": "network_spike_triggered"}