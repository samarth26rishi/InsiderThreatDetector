# 🔐 Insider Threat Detection System  
### Behavioral Anomaly Detection using Machine Learning & Explainable AI

---

## 📌 Overview

This project implements a multi-month insider threat detection framework that identifies anomalous employee behavior using:

- 🧠 Isolation Forest (unsupervised anomaly detection)
- 👤 Personal historical deviation tracking
- 📊 Organizational drift detection
- 🧬 Psychometric risk modeling (OCEAN traits)
- 🔍 SHAP explainability for model transparency
- 📈 Interactive Streamlit dashboard

The system trains on an initial baseline month (**Month 0**) and continuously monitors employees in subsequent months.

---

## 🧠 Problem Statement

Insider threats are difficult to detect because:

- Malicious actions often resemble legitimate work
- Attackers may act gradually
- Coordinated group behavior can bypass simple thresholds
- Employees naturally change behavior during deadlines or peak periods

This project simulates and detects:

- Individual abnormal spikes
- Long-term behavioral deviation
- Coordinated data exfiltration attempts
- Organization-wide behavioral drift

---

## 🏗️ System Architecture

### Phase 1 — Baseline Month (Month 0)

- Aggregates daily email & USB activity
- Normalizes behavior per day
- Merges psychometric traits
- Trains Isolation Forest model
- Saves:
  - Personal behavioral baseline
  - Organizational baseline statistics
  - Scaler + trained model

---

### Phase 2 — Monitoring (Month 1+)

For each simulated day:

1. Update cumulative behavior
2. Compare users against:
   - Peer group (Isolation Forest anomaly detection)
   - Their own historical baseline
   - Psychometric risk amplification
3. Detect:
   - Individual anomalies
   - Coordinated group behavior
   - Organizational drift
4. Provide SHAP explanation of flagged users

---

## 📊 Features Used

### Behavioral Features (Primary Weight)

- `total_emails`
- `external_emails`
- `attachments_sent`
- `bcc_in_email`
- `avg_email_size`
- `usb_insertions`
- `files_accessed`
- `sensitive_files_accessed`

Email-based behavior carries stronger influence in anomaly detection.

---

### Psychometric Features (Secondary Weight)

- Openness (O)
- Conscientiousness (C — inverted for risk modeling)
- Extraversion (E)
- Agreeableness (A — inverted for risk modeling)
- Neuroticism (N)

Psychometrics act as contextual risk amplifiers rather than primary drivers.

---

## 🚨 Threat Detection Logic

A user is flagged if:

- Isolation Forest detects abnormal peer deviation  
**OR**
- The user deviates significantly from their own historical baseline  
**OR**
- Psychometric risk + anomaly combination exceeds threshold  

Additionally:

- Coordinated attacks are detected via organizational drift ratio
- Organization-wide sensitive file spikes trigger alerts
- Group anomaly percentage is monitored

---

## 📈 Dashboard Capabilities

The Streamlit dashboard provides:

- 📊 Anomaly score distribution histogram
- 📉 Organizational drift tracking
- 🚨 Coordinated attack alerts
- 👤 Personal deviation indicators
- 🔍 SHAP feature impact visualization
- 🏆 Ranked list of high-risk users
- 📈 Multi-day behavioral trend tracking

---

## 📂 Project Structure
month_0_email/
month_0_usbfiles/
month_1_email/
month_1_usbfiles/
month_2_email/
month_2_usbfiles/

app.py
make_model_repeated.py
full_generator.py

email.csv
file_usb_activity.csv
psychometric.csv

---

## ▶️ How To Run

### 1️⃣ Install Dependencies
pip install -r requirements.txt

### 2️⃣ (Optional) Generate Multi-Month Simulation Data
python full_generator.py

### 3️⃣ Run the Dashboard
streamlit run app.py

Month 0 will build the baseline automatically.  
Month 1+ will begin monitoring and detecting anomalies.

---

## 📚 Dataset

This project uses:

- Public email activity dataset (Kaggle)
- Public file/USB activity dataset (Kaggle)
- Psychometric traits mapped to users for behavioral modeling

Datasets are used strictly for academic and research purposes.

---

## 🎓 Academic Context

Developed as an undergraduate cybersecurity + machine learning systems project.

Demonstrates:

- Unsupervised anomaly detection
- Behavioral feature engineering
- Multi-phase model retraining
- Personal vs peer comparison modeling
- Coordinated attack detection logic
- Explainable AI integration
- Interactive ML dashboard development

---

## 🚀 Future Improvements

- Graph-based coordinated attack modeling
- Real-time streaming architecture
- Temporal deep learning models (LSTM)
- Role-aware behavioral baselines
- Enterprise API deployment

---

## 👨‍💻 Author

Undergraduate Project — Cybersecurity & Machine Learning
=======
# InsiderThreatDetector
Multi-layer Insider Threat Detection System using Isolation Forest, psychometric risk modeling, behavioral baselines, organizational drift detection, and SHAP explainability — built with Python and Streamlit.

