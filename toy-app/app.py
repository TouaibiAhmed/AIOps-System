from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

import time
import multiprocessing



app = FastAPI()

Instrumentator().instrument(app).expose(app)

# Variable globale pour simuler une fuite mémoire
memory_leak_list = []

def burn(duration):
    end_time = time.time() + duration
    while time.time() < end_time:
        _ = 999999 ** 2

@app.get("/")
def health():
    return {"status": "ok"}



@app.get("/stress-cpu")
def stress_cpu(duration: int = 20, cores: int = 1):
    for _ in range(cores):
        p = multiprocessing.Process(target=burn, args=(duration,))
        p.start()
    return {"action": "cpu_stress_started", "duration": duration, "cores": cores}

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
def network_spike(requests_count: int = 500):
    import requests
    for _ in range(requests_count):
        try:
            requests.get("https://pypi.org", timeout=1)
        except Exception:
            pass
    return {"action": "network_spike_triggered"}