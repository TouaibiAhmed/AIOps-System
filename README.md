# 🚀 AIOps Platform for Intelligent Infrastructure Monitoring and Incident Detection

## 📌 Overview

This project is an **Artificial Intelligence for IT Operations (AIOps)** platform designed to automatically monitor system infrastructure, detect anomalies, classify incidents, and visualize system health in real time.

Unlike traditional monitoring solutions that rely on fixed thresholds (e.g., CPU > 90%), this platform leverages **Machine Learning** to learn normal system behavior and identify abnormal patterns such as CPU saturation, memory leaks, and network spikes without manually defined thresholds.

The project simulates a complete production monitoring pipeline using **Docker**, **Prometheus**, **Grafana**, **FastAPI**, and **Machine Learning models**.

---

# 🎯 Objectives

The main objective is to build an end-to-end AIOps pipeline capable of:

* Collecting infrastructure metrics automatically.
* Simulating realistic infrastructure incidents.
* Detecting anomalies using unsupervised Machine Learning.
* Classifying detected incidents into predefined categories.
* Exposing predictions through a REST API.
* Visualizing metrics and alerts through interactive dashboards.

---

# 🏗️ System Architecture

```
                     Docker Environment
                            │
                            ▼
                   +-------------------+
                   |      Toy App      |
                   | (Simulated Server)|
                   +-------------------+
                            │
                Chaos Script Generates Incidents
                            │
                            ▼
         +---------------------------------------+
         | Node Exporter & cAdvisor              |
         | Collect Host & Container Metrics      |
         +---------------------------------------+
                            │
                            ▼
                    +----------------+
                    |  Prometheus    |
                    | Metrics Storage|
                    +----------------+
                            │
               +------------+------------+
               │                         │
               ▼                         ▼
          ETL Pipeline             Grafana Dashboard
               │
               ▼
      Data Preprocessing & Feature Engineering
               │
               ▼
     Isolation Forest (Anomaly Detection)
               │
               ▼
 Random Forest / XGBoost (Incident Classification)
               │
               ▼
            FastAPI REST API
               │
               ▼
      Dashboard / Alerting System
```

---

# ⚙️ Technology Stack

## Infrastructure

* Docker
* Docker Compose

## Monitoring

* Prometheus
* Grafana
* Node Exporter
* cAdvisor

## Backend

* Python
* FastAPI
* Uvicorn

## Machine Learning

* Pandas
* NumPy
* Scikit-learn
* TensorFlow / Keras (optional)
* XGBoost

## Database

* PostgreSQL
* TimescaleDB (optional)

---

# 📂 Project Structure

```
aiops-project/
│
├── docker-compose.yml
│
├── prometheus/
│   └── prometheus.yml
│
├── toy-app/
│   ├── app.py
│   └── requirements.txt
│
├── chaos/
│   └── chaos_script.py
│
├── etl/
│   └── extract_prometheus.py
│
├── ml/
│   ├── preprocessing.py
│   ├── train_detection.py
│   ├── train_classification.py
│   └── models/
│
├── api/
│   ├── main.py
│   └── requirements.txt
│
├── dashboard/
│
├── data/
│
├── notebooks/
│
└── README.md
```

---

# 🔄 Workflow

## 1. Infrastructure Monitoring

Docker starts all monitoring services:

* Prometheus
* Grafana
* Node Exporter
* cAdvisor

Node Exporter collects operating system metrics while cAdvisor monitors Docker containers.

---

## 2. Incident Simulation

A lightweight FastAPI Toy App simulates a production server.

The Chaos Script periodically generates controlled incidents such as:

* CPU Saturation
* Memory Leak
* Network Spike
* Normal Operation

Each generated incident is timestamped and automatically labeled.

---

## 3. Data Collection

Prometheus scrapes metrics every **15 seconds** including:

* CPU Usage
* Memory Usage
* Disk Usage
* Network Traffic

These metrics are extracted through the ETL pipeline and stored as CSV datasets.

---

## 4. Data Processing

The preprocessing stage:

* Cleans missing values
* Aligns timestamps
* Normalizes numerical features
* Generates rolling statistics
* Merges infrastructure metrics with incident labels

---

## 5. Machine Learning

### Anomaly Detection

Isolation Forest is trained to distinguish:

* Normal
* Anomalous

without requiring labeled anomaly data.

---

### Incident Classification

Once an anomaly is detected, a supervised classifier predicts its cause:

* CPU Saturation
* Memory Leak
* Network Spike

Random Forest is used as the baseline classifier.

---

## 6. Prediction API

A FastAPI REST API loads the trained models and exposes:

```
GET /health

POST /predict
```

The API returns:

```json
{
  "anomaly": true,
  "incident_type": "cpu"
}
```

---

## 7. Visualization

Grafana dashboards display:

* CPU Usage
* Memory Usage
* Network Traffic
* Anomaly Score
* Incident Type
* Alerts

---

# 🚀 Getting Started

## Clone Repository

```bash
git clone https://github.com/yourusername/aiops-project.git
cd aiops-project
```

---

## Create Python Environment

```bash
python -m venv venv
```

Linux / macOS

```bash
source venv/bin/activate
```

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Start Monitoring Stack

```bash
docker compose up -d
```

Verify services:

| Service       | URL                   |
| ------------- | --------------------- |
| Prometheus    | http://localhost:9090 |
| Grafana       | http://localhost:3000 |
| Node Exporter | http://localhost:9100 |
| cAdvisor      | http://localhost:8080 |

---

## Run the Toy App

```bash
cd toy-app

uvicorn app:app --host 0.0.0.0 --port 8000
```

---

## Run Chaos Engineering

```bash
python chaos/chaos_script.py
```

---

## Extract Metrics

```bash
python etl/extract_prometheus.py
```

---

## Train Models

Detection model

```bash
python ml/train_detection.py
```

Classification model

```bash
python ml/train_classification.py
```

---

## Start Prediction API

```bash
cd api

uvicorn main:app --host 0.0.0.0 --port 8001
```

---

# 📊 Machine Learning Pipeline

```
Infrastructure Metrics
          │
          ▼
Data Cleaning
          │
          ▼
Feature Engineering
          │
          ▼
Isolation Forest
          │
   Is anomaly?
     /      \
   No        Yes
   │          │
 Normal   Random Forest
               │
               ▼
      CPU / Memory / Network
```

---

# 📈 Expected Results

* Automatic anomaly detection
* Root cause classification
* Real-time monitoring
* REST API predictions
* Interactive dashboards
* Alert generation
* Historical metrics storage

---

# 📌 Future Improvements

* Kubernetes deployment
* LSTM Autoencoder anomaly detection
* Self-healing automation
* Email and Slack notifications
* Explainable AI (SHAP)
* Log analysis integration
* Multi-node monitoring

---

# 👨‍💻 Author

**AI & Data Science Engineering Project**

Developed as an end-to-end AIOps platform combining Infrastructure Monitoring, Machine Learning, and Cloud-Native technologies.

---

# 📄 License

This project is intended for educational and research purposes.
