# 🏥 Smart Hospital Patient Management & Prescription System

This project is a **Flask + MongoDB-based hospital management platform** that integrates patient records, prescription scanning, and doctor assignment. It also connects with hardware health monitoring devices (ECG, SpO2, Heart Rate, etc.) for real-time updates.

---

## 🚀 Features
- **Patient Management**
  - Add new patients via API or frontend form.
  - Assigns doctors automatically based on disease specialty.
  - Stores patient details in MongoDB.

- **Doctor Management**
  - Stores available doctors and their specialties.
  - Ensures only available doctors are assigned.
  
- **Prescription OCR**
  - Upload a prescription image.
  - Extract medicines and dosage using AI.
  - Calculate required number of tablets (e.g., 3x daily for 7 days = 21 tablets).
  - Add medicines to cart and show total payment.

- **Hardware Health Monitoring**
  - ECG signal plotted in real-time.
  - Other health metrics (BPM, SpO2, Blood Pressure, Stress) updated numerically.
  - Data accessible through `/data` and `/graph` endpoints.

---

## 🛠️ Tech Stack
- **Backend**: Python Flask
- **Database**: MongoDB
- **AI/ML**: OpenAI (GPT-4o) or Hugging Face OCR
- **Frontend**: HTML, JavaScript, CSS
- **Hardware**: ESP32 + Sensors (ECG, SpO2, Temp, BP, etc.)

---

## ⚡ How to Use
### 1. Install Requirements
```bash
pip install flask pymongo python-dotenv openai flask-cors
The server will run on http://127.0.0.1:5000/.

4. Access Endpoints

POST /patients → Add patient
GET /patients → Get all patients
GET /doctors → Get all doctors
POST /scan → Upload prescription image
POST /cart → Add extracted medicines to cart
GET /showcart → See total items & cost

Hardware Integration

ESP32 collects sensor data (ECG, SpO2, BPM, etc.).
Data is exposed as JSON via /data endpoint.
/graph shows ECG signal in real-time.
Flask server connects hardware + AI + frontend.

Safety Features


Data Security

API keys stored in environment variables.
MongoDB connection secured via URI, not hardcoded.
HTTPS can be enabled in production.

False Positive Reduction

Multi-step OCR → Prescription validated against medicine database.
Dosage parsing double-checked by rule-based filters.
Alerts if prescription text is unclear.


System Reliability
Doctor assignment only from available pool.
Logs stored in MongoDB for future audits.
Error handling for sensor dropouts.


False Positive Measures

OCR Validation → If extracted text is ambiguous, asks for confirmation.
Threshold-based Health Data → Example: If ECG shows abnormal BPM (<40 or >200), system flags as potential error.
Redundancy → If one sensor fails, data still collected from others.
Doctor Review → Final confirmation is required from medical staff before treatment.


Contributors

Aranya Bandhu – Lead AI Developer & Hardware Developer 

Ayush Pundhir – AI & Web Integration
