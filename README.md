🚀 AI-Enabled Nightly Telemetry Test Tool for CubeSat Health Monitoring
HEX20 Flight Software Internship – Problem Statement I

This project implements an AI-enabled telemetry analysis system, designed according to the Flight Software Internship Problem Statement provided by HEX20.

The tool performs:

🛰 Telemetry generation → saved as binary packet

🧠 AI-based anomaly detection using Isolation Forest

📈 Visualization using Tkinter + Matplotlib

🕒 Nightly scheduled processing (custom scheduler, no external libraries)

👨‍💻 Interactive GUI with logs, plots, and daily result navigation

🗂 Project Structure
HEX20-CubeSat-Nightly-AI-Telemetry-Tool/
│
├── gui_tk.py                 # Tkinter dashboard GUI
├── nightly_processor.py       # AI anomaly detection + rule-based checks
├── generate_telemetry.py      # Binary telemetry generator
├── scheduler.py               # Custom nightly scheduler
│
├── telemetry/                 # Auto-generated .bin files
├── results/                   # Daily JSON analysis reports
│
└── README.md                  # Documentation
Installation
1. Clone Repository
git clone https://github.com/<your-username>/HEX20-CubeSat-Nightly-AI-Telemetry-Tool.git
cd HEX20-CubeSat-Nightly-AI-Telemetry-Tool

2. Install Dependencies
pip install -r requirements.txt


requirements.txt

numpy
pandas
scikit-learn
matplotlib


(Tkinter is built into Python on Windows/macOS.)

▶️ Usage
Run GUI:
python gui_tk.py

Run Telemetry Generator Manually:
python generate_telemetry.py

Run Nightly Processor Manually:
python nightly_processor.py

Run Scheduler (optional):
python scheduler.py

🧠 AI Engine
✔ Isolation Forest

Used for unsupervised anomaly detection:

Detects overheating

Battery voltage drops

CPU overload

Attitude instability

✔ Rule-Based Alerts

Voltage must be 7.0–8.4 V

Temperature within –10°C to 50°C

CPU < 95%

Attitude error < 4.5°

🖥️ GUI Features (Tkinter)

Status indicator (NORMAL / ANOMALY)

Daily telemetry table

AI score + alerts

Trend plots (battery, temperature, CPU, attitude)

Anomalies shown as red dots

"Run Test Now" button

Log viewer

⏰ Scheduler

A custom time-based scheduler (Python-only) runs nightly tests without relying on external libraries, ensuring compatibility with Python 3.13.
🧩 Future Enhancements

Integrate with actual onboard telemetry sources

Email/SMS alerts

Multi-sensor packet support

Replace Isolation Forest with time-series models
