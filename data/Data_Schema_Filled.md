# Data Schema — Digital Arrest Fraud Detection System

**Source patterns:** Compiled from real digital arrest case reports (CBI/ED/Customs impersonation cases, 2024-2026, MHA/Supreme Court probe data)

## 1. Call Metadata Schema

| Field | Type | Description | Sample Value |
|---|---|---|---|
| call_id | string (UUID) | Unique identifier for the call | "c_8821a" |
| caller_number | string | Phone number / spoofed origin | "+92XXXXXXXXX" (or spoofed Indian number) |
| receiver_id | string | Anonymized user ID | "u_4471" |
| call_timestamp | datetime | Start time | "2026-07-01T10:32:00Z" |
| call_duration_sec | integer | Length of call | up to 86400+ (cases ran 4-40 hours) |
| transcript_text | string | Speech-to-text transcript | "This is CBI Mumbai. A parcel under your name contains drugs and fake passports..." |
| caller_claimed_identity | enum | Impersonated authority | "CBI" / "ED" / "Customs" / "RBI" / "Mumbai Police" / "TRAI" |
| accusation_type | enum | Crime victim is accused of | "money_laundering" / "drug_trafficking" / "parcel_with_contraband" / "aadhaar_misuse" |
| fake_document_shown | boolean | FIR / warrant / court order shown on screen | true |
| video_call_flag | boolean | Conducted via Skype/WhatsApp video | true |
| isolation_flag | boolean | Told not to disconnect / not to tell family | true |
| payment_destination_claim | string | Where victim told to send money | "RBI escrow account" / "verification account" |
| urgency_flag | boolean | High-pressure, time-bound language detected | true |

## 2. Transaction Log Schema

| Field | Type | Description | Sample Value |
|---|---|---|---|
| transaction_id | string (UUID) | Unique transaction ID | "t_5523b" |
| account_id | string | Sender (victim) account | "acc_9912" |
| amount | float | Amount transferred | Real cases ranged ₹1.7L to ₹12 crore |
| currency | string | Currency | "INR" |
| transaction_timestamp | datetime | When sent | "2026-07-01T10:41:00Z" |
| linked_call_id | string (nullable) | FK to the scam call, if any | "c_8821a" |
| destination_account_flag | enum | Risk signal on receiving account | "new_account_<7days" / "mule_account_pattern" / "multiple_unrelated_senders" |
| destination_account_age_days | integer | Age of receiving account | e.g. 3 |
| layering_hops_detected | integer | Number of accounts money passed through before exit | e.g. 4 (real cases show multi-layer mule networks) |

## 3. Fraud Network Graph

| Field | Type | Description |
|---|---|---|
| node_id | string | Account / phone number / device ID |
| node_type | enum | "account" / "phone_number" / "device_id" |
| edge_source → edge_target | string | Money flow direction |
| edge_weight | float | Transaction volume between nodes |
| risk_score | float (0-1) | Likelihood node is part of a mule network |
| cluster_id | string | Group ID for connected fraud rings (real cases show these as organized syndicate networks, often traced to Southeast Asia) |

## 4. Output / Prediction Schema

| Field | Type | Description |
|---|---|---|
| session_id | string | Links call + transaction |
| scam_probability | float (0-1) | Classifier confidence |
| key_triggers | array | Which flags fired — e.g. ["isolation_flag", "fake_document_shown", "urgency_flag"] |
| lead_time_sec | integer | Time between detection and attempted transfer |
| evidence_package | JSON | Transcript excerpt + flags + timestamps + destination account flags, structured for legal admissibility |
