import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# -----------------------------
# Load Data
# -----------------------------
def load_data(path="data/synthetic_calls.json"):
    with open(path, "r") as f:
        return json.load(f)


# -----------------------------
# Feature Extraction
# -----------------------------
def extract_flags(transcript):
    text = transcript.lower()

    return {
        "urgency_flag": any(word in text for word in ["immediately", "urgent", "now"]),
        "isolation_flag": any(word in text for word in ["do not disconnect", "stay on call", "do not inform"]),
    }


# -----------------------------
# Scam Scoring Logic
# -----------------------------
def compute_scam_score(call):
    score = 0

    if call["caller_claimed_identity"] in ["CBI", "ED", "Mumbai Police", "Customs", "RBI"]:
        score += 0.2

    if call["accusation_type"] in [
        "money_laundering",
        "drug_trafficking",
        "parcel_with_contraband",
        "aadhaar_misuse"
    ]:
        score += 0.2

    if call.get("video_call_flag"):
        score += 0.15

    if call.get("fake_document_shown"):
        score += 0.15

    if call.get("isolation_flag"):
        score += 0.15

    if call.get("urgency_flag"):
        score += 0.1

    if "escrow" in call["payment_destination_claim"].lower():
        score += 0.05

    # Duration signal
    duration = call.get("call_duration_sec", 0)

    if duration > 7200:
        score += 0.1
    elif duration > 1800:
        score += 0.05

    return round(min(score, 1.0), 2)


# -----------------------------
# EXISTING FUNCTION (UNCHANGED)
# -----------------------------
def analyze_calls():
    data = load_data()
    results = []

    for call in data:
        extracted_flags = extract_flags(call["transcript_text"])
        call.update(extracted_flags)

        scam_prob = compute_scam_score(call)

        triggers = [k for k, v in call.items() if k.endswith("_flag") and v]

        results.append({
            "call_id": call["call_id"],
            "scam_probability": scam_prob,
            "key_triggers": triggers
        })

    return results


# -----------------------------
# 🔥 NEW: API ROUTE (MINIMAL ADD)
# -----------------------------
@app.route('/analyze', methods=['POST'])
def analyze():
    call = request.json

    extracted_flags = extract_flags(call["transcript_text"])
    call.update(extracted_flags)

    scam_prob = compute_scam_score(call)

    triggers = [k for k, v in call.items() if k.endswith("_flag") and v]

    result = {
        "scam_probability": scam_prob,
        "key_triggers": triggers
    }

    return jsonify(result)


# -----------------------------
# 🔥 UPDATED RUN (API MODE)
# -----------------------------
import os

if __name__ == '__main__':
    # Render provides a PORT environment variable. If it's not there, default to 5000 locally.
    port = int(os.environ.get("PORT", 5000))
    
    # Crucial: Change host to '0.0.0.0'
    app.run(host='0.0.0.0', port=port)
