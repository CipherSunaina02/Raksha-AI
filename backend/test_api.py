import requests

url = "http://127.0.0.1:5000/analyze"

data = {
    "caller_claimed_identity": "CBI",
    "accusation_type": "drug_trafficking",
    "payment_destination_claim": "RBI escrow account",
    "transcript_text": "Do not disconnect. Transfer money immediately.",
    "video_call_flag": True,
    "fake_document_shown": True,
    "isolation_flag": True,
    "urgency_flag": True,
    "call_duration_sec": 7200
}

res = requests.post(url, json=data)
print(res.json())