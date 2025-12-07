import struct
from datetime import datetime
import random
from pathlib import Path

# Telemetry field names
FIELDS = ["battery_voltage", "battery_current", "temperature",
          "cpu_usage", "attitude_error"]


def generate_sample_values():
    """Simulate a single snapshot of CubeSat health telemetry."""
    battery_voltage = random.uniform(7.0, 8.4)
    battery_current = random.uniform(0.1, 1.5)
    temperature = random.uniform(-5, 40)
    cpu_usage = random.uniform(10, 90)
    attitude_error = random.uniform(0.0, 5.0)
    return [battery_voltage, battery_current, temperature, cpu_usage, attitude_error]


def generate_and_save_telemetry(output_dir="telemetry"):
    """
    Generate one telemetry packet and save it as a binary file.
    Packet format: 5 x float32 (big endian) -> 20 bytes.
    """
    Path(output_dir).mkdir(exist_ok=True)
    values = generate_sample_values()
    packet = struct.pack("!5f", *values)

    filename = datetime.now().strftime("telemetry_%Y%m%d.bin")
    filepath = Path(output_dir) / filename

    with open(filepath, "wb") as f:
        f.write(packet)

    return str(filepath), dict(zip(FIELDS, values))


if __name__ == "__main__":
    path, vals = generate_and_save_telemetry()
    print("Telemetry saved to:", path)
    print("Values:", vals)
