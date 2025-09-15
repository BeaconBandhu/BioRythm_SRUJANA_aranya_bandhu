import requests
import json
import joblib
import numpy as np

# ---------------------------
# 1. Fetch Data from ESP32
# ---------------------------
ESP32_IP = "http://192.168.171.117"

def fetch_ecg_data():
    try:
        response = requests.get(f"{ESP32_IP}/graph", timeout=5)
        if response.status_code == 200:
            return response.json().get("ecg", [])
        return []
    except Exception as e:
        print("Error fetching ECG:", e)
        return []

def fetch_vitals_data():
    try:
        response = requests.get(f"{ESP32_IP}/data", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception as e:
        print("Error fetching Vitals:", e)
        return {}

# ---------------------------
# 2. ML Classification
# ---------------------------
def classify_patient(ecg, vitals):
    try:
        model = joblib.load("patient_classifier.pkl")
    except:
        # Dummy rule-based classifier if no model is trained
        def dummy_model(features):
            if features[0] < 92:
                return "Critical"
            elif features[1] > 100:
                return "Tachycardia"
            else:
                return "Stable"
        model = dummy_model

    hr = vitals.get("BPM", 80)  # assuming your ESP32 sends BPM in /data
    spo2 = vitals.get("SpO2", 98)

    features = [spo2, hr]

    if callable(model):
        status = model(features)
    else:
        status = model.predict([features])[0]

    return status, hr

# ---------------------------
# 3. JSON Output
# ---------------------------
def generate_patient_report():
    ecg_signal = fetch_ecg_data()
    vitals = fetch_vitals_data()

    if not vitals:
        return json.dumps({"error": "No data received from ESP32"}, indent=4)

    status, hr = classify_patient(ecg_signal, vitals)

    report = {
        "PatientStatus": status,
        "HeartRate": hr,
        "ECGSignal": ecg_signal[:100],  # send first 100 samples only for JSON
        "Vitals": vitals
    }
    return json.dumps(report, indent=4)

# ---------------------------
# Main Execution
# ---------------------------
if __name__ == "__main__":
    print(generate_patient_report())
