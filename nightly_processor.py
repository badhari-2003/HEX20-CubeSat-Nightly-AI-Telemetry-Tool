import struct
import glob
import json
from datetime import datetime
from pathlib import Path

import numpy as np
from sklearn.ensemble import IsolationForest

from generate_telemetry import FIELDS, generate_and_save_telemetry

RESULTS_DIR = "results"
TELEMETRY_DIR = "telemetry"


def read_latest_packet():
    files = sorted(glob.glob(f"{TELEMETRY_DIR}/telemetry_*.bin"))
    if not files:
        raise FileNotFoundError("No telemetry files found. Generate telemetry first.")
    latest = files[-1]
    with open(latest, "rb") as f:
        data = f.read()
    if len(data) != 20:
        raise ValueError(
            f"Unexpected packet size in {latest}. Expected 20 bytes, got {len(data)}."
        )
    values = struct.unpack("!5f", data)
    return latest, np.array(values).reshape(1, -1)


def load_or_train_model():
    # Synthetic "normal" operating data
    np.random.seed(0)
    normal_data = np.column_stack(
        (
            np.random.uniform(7.4, 8.2, 200),  # battery_voltage
            np.random.uniform(0.2, 1.2, 200),  # battery_current
            np.random.uniform(5, 30, 200),     # temperature
            np.random.uniform(20, 80, 200),    # cpu_usage
            np.random.uniform(0.0, 3.0, 200),  # attitude_error
        )
    )
    model = IsolationForest(contamination=0.03, random_state=0)
    model.fit(normal_data)
    return model


def rule_checks(values):
    v = dict(zip(FIELDS, values.flatten().tolist()))
    alerts = []
    if not (7.0 <= v["battery_voltage"] <= 8.4):
        alerts.append("Battery voltage out of range")
    if not (-10 <= v["temperature"] <= 50):
        alerts.append("Temperature out of range")
    if v["cpu_usage"] > 95:
        alerts.append("CPU usage too high")
    if v["attitude_error"] > 4.5:
        alerts.append("Attitude error too high")
    return alerts


def process_nightly(auto_generate=True):
    """
    Run one full cycle:
    - Optionally generate new telemetry and save to .bin
    - Read latest telemetry packet
    - Run AI anomaly detection + rule checks
    - Save JSON result in results/
    """
    Path(RESULTS_DIR).mkdir(exist_ok=True)

    if auto_generate:
        latest_file, last_values = generate_and_save_telemetry(output_dir=TELEMETRY_DIR)
    else:
        latest_file, arr = read_latest_packet()
        last_values = dict(zip(FIELDS, arr.flatten().tolist()))

    # Use most recent telemetry for analysis
    _, values_arr = read_latest_packet()
    model = load_or_train_model()
    scores = model.decision_function(values_arr)
    preds = model.predict(values_arr)  # 1 = normal, -1 = anomaly

    alerts = rule_checks(values_arr)
    is_anomaly = preds[0] == -1

    result = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "source_file": latest_file,
        "telemetry": last_values,
        "is_anomaly": bool(is_anomaly),
        "ai_score": float(scores[0]),
        "rule_alerts": alerts,
    }

    out_name = datetime.now().strftime(f"{RESULTS_DIR}/result_%Y%m%d.json")
    with open(out_name, "w") as f:
        json.dump(result, f, indent=2)

    return out_name, result


if __name__ == "__main__":
    path, res = process_nightly(auto_generate=True)
    print("Result saved to:", path)
    print(res)
