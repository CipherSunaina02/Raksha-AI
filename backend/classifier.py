import json

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
        "urgency_flag": any(word in text for word in ["immediately", "urgent", "within 1 hour"]),
        "isolation_flag": any(word in text for word in ["do not disconnect", "stay on call", "do not inform"]),
    }


# -----------------------------
# Scam Scoring Logic
# -----------------------------
def compute_scam_score(call):
    score = 0

    # Identity check
    if call["caller_claimed_identity"] in ["CBI", "ED", "Mumbai Police", "Customs", "RBI"]:
        score += 0.2

    # Accusation check
    if call["accusation_type"] in [
        "money_laundering",
        "drug_trafficking",
        "parcel_with_contraband",
        "aadhaar_misuse"
    ]:
        score += 0.2

    # Behavioral flags
    if call.get("video_call_flag"):
        score += 0.15

    if call.get("fake_document_shown"):
        score += 0.15

    if call.get("isolation_flag"):
        score += 0.15

    if call.get("urgency_flag"):
        score += 0.1

    # Payment pattern
    if "escrow" in call["payment_destination_claim"].lower():
        score += 0.05

    return round(min(score, 1.0), 2)


# -----------------------------
# Main Prediction Function
# -----------------------------
def analyze_calls():
    data = load_data()
    results = []

    for call in data:
        # Extract flags from transcript
        extracted_flags = extract_flags(call["transcript_text"])

        # Merge extracted flags into call
        call.update(extracted_flags)

        # Compute score
        scam_prob = compute_scam_score(call)

        # Collect triggered flags
        triggers = [k for k, v in call.items() if k.endswith("_flag") and v]

        results.append({
            "call_id": call["call_id"],
            "scam_probability": scam_prob,
            "key_triggers": triggers
        })

    return results


# -----------------------------
# Run Test
# -----------------------------
if __name__ == "__main__":
    output = analyze_calls()

    for o in output:
        print(o)