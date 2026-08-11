import json
import sys
import re

LOG_FILE = "data/logs.jsonl"
SLO_LATENCY = 3000

# Regex cơ bản tìm PII: email hoặc credit card
EMAIL_REGEX = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
CC_REGEX = re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b")

def detect():
    anomalies = []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                
                # Check Latency
                latency = record.get("latency_ms")
                if latency and latency > SLO_LATENCY:
                    anomalies.append(f"[Line {line_no}] LATENCY ANOMALY: {latency}ms exceeds SLO {SLO_LATENCY}ms (Trace: {record.get('correlation_id')})")
                
                # Check Error
                if record.get("level") == "error" or record.get("event") == "request_failed":
                    anomalies.append(f"[Line {line_no}] ERROR ANOMALY: {record.get('error_type', 'Unknown Error')} (Trace: {record.get('correlation_id')})")
                
                # Check PII in payloads
                payload = str(record.get("payload", ""))
                if EMAIL_REGEX.search(payload):
                    anomalies.append(f"[Line {line_no}] PII LEAK (Email): Detected in payload (Trace: {record.get('correlation_id')})")
                if CC_REGEX.search(payload):
                    anomalies.append(f"[Line {line_no}] PII LEAK (Credit Card): Detected in payload (Trace: {record.get('correlation_id')})")
                    
    except FileNotFoundError:
        print(f"File {LOG_FILE} not found.")
        sys.exit(1)

    if anomalies:
        print("=== ANOMALIES DETECTED ===")
        for a in anomalies:
            print(a)
    else:
        print("No anomalies detected.")

if __name__ == "__main__":
    detect()
