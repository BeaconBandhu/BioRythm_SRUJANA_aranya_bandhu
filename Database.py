from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import random
from flask_cors import CORS   # <-- import

# --- Flask App ---
app = Flask(__name__)
CORS(app)   # <-- enable CORS for all routes

# --- MongoDB Connection ---
client = MongoClient("mongodb://localhost:27017/")
db = client.hospital_records
patients_collection = db.patients
doctors_collection = db.doctors

# --- Helper function for doctor assignment ---
def get_available_doctor(specialty):
    """
    Finds and assigns a random available doctor based on specialty.
    """
    available_doctors = list(doctors_collection.find({
        "is_available": True,
        "specialty": specialty
    }))
    
    if available_doctors:
        return random.choice(available_doctors)["name"]
    return "Not Assigned (No available doctor)"

# --- API Endpoints ---

@app.route('/patients', methods=['POST'])
def add_patient_api():
    """
    API endpoint to add a new patient from the frontend.
    """
    data = request.json
    required_fields = ["patient_name", "disease_type", "criticality_status", "room_number"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    doctor = get_available_doctor(data["disease_type"])
    
    patient_document = {
        "patient_name": data["patient_name"],
        "doctor_assigned": doctor,
        "disease_type": data["disease_type"],
        "criticality_status": data["criticality_status"],
        "room_number": data["room_number"],
        "check_in_date": datetime.now()
    }
    
    result = patients_collection.insert_one(patient_document)
    return jsonify({"message": "Patient record added successfully", "id": str(result.inserted_id)}), 201

@app.route('/patients', methods=['GET'])
def get_all_patients():
    """
    API endpoint to retrieve all patient records.
    """
    patients = []
    for patient in patients_collection.find():
        patient['_id'] = str(patient['_id'])
        patients.append(patient)
    return jsonify(patients), 200

@app.route('/doctors', methods=['GET'])
def get_all_doctors():
    """
    API endpoint to retrieve all doctor records.
    """
    doctors = []
    for doctor in doctors_collection.find({}, {"_id": 0}):
        doctors.append(doctor)
    return jsonify(doctors), 200

# --- Main ---
if __name__ == "__main__":
    # Add some sample doctors if not already in DB
    if doctors_collection.count_documents({}) == 0:
        print("No doctors found. Creating sample doctor records...")
        doctors_collection.insert_many([
            {"name": "Dr. Aranya", "specialty": "Cardiology", "is_available": True},
            {"name": "Dr. Pratik", "specialty": "Neurology", "is_available": True},
            {"name": "Dr. Sandeep", "specialty": "Oncology", "is_available": True},
            {"name": "Dr. Meera", "specialty": "Pediatrics", "is_available": True},
        ])
    app.run(host='0.0.0.0', port=5002, debug=True)
