import json
import glob
from pathlib import Path
from datetime import datetime

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import pandas as pd

from nightly_processor import process_nightly, RESULTS_DIR
from generate_telemetry import FIELDS


class NightlyHealthGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CubeSat Nightly Telemetry – AI Health Monitor")
        self.root.geometry("1000x700")

        # --- Header ---
        header = tk.Frame(root, bg="#1f2933", pady=10)
        header.pack(fill="x")
        tk.Label(
            header,
            text="CubeSat Nightly Telemetry – AI Health Monitor",
            font=("Helvetica", 16, "bold"),
            bg="#1f2933",
            fg="white",
        ).pack()

        # --- Controls ---
        control = tk.Frame(root, pady=10)
        control.pack(fill="x")

        self.run_button = ttk.Button(
            control,
            text="Run Test Now (Generate + Analyze)",
            command=self.run_manual_test,
        )
        self.run_button.pack(side="left", padx=10)

        self.refresh_button = ttk.Button(
            control,
            text="Refresh Results",
            command=self.refresh_results,
        )
        self.refresh_button.pack(side="left", padx=10)

        self.status_label = tk.Label(
            control,
            text="Status: IDLE",
            font=("Helvetica", 12),
            fg="gray",
        )
        self.status_label.pack(side="left", padx=10)

        # --- Date selection ---
        date_frame = tk.Frame(root)
        date_frame.pack(fill="x", padx=10)

        tk.Label(date_frame, text="Select Date:").pack(side="left")
        self.date_var = tk.StringVar()
        self.date_combo = ttk.Combobox(
            date_frame, textvariable=self.date_var, state="readonly"
        )
        self.date_combo.pack(side="left", padx=5)
        self.date_combo.bind(
            "<<ComboboxSelected>>",
            lambda e: self.update_view_for_selected_date(),
        )

        # --- Plot area ---
        plot_frame = tk.Frame(root)
        plot_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.fig = Figure(figsize=(6, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Telemetry Parameters Over Days")
        self.ax.set_xlabel("Date index")
        self.ax.set_ylabel("Scaled value")

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # --- Logs / Details ---
        bottom = tk.Frame(root)
        bottom.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Left: Telemetry table
        table_frame = tk.LabelFrame(bottom, text="Telemetry Snapshot (Selected Day)")
        table_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.tree = ttk.Treeview(
            table_frame, columns=("param", "value"), show="headings", height=6
        )
        self.tree.heading("param", text="Parameter")
        self.tree.heading("value", text="Value")
        self.tree.column("param", width=150)
        self.tree.column("value", width=120)
        self.tree.pack(fill="both", expand=True)

        # Right: Logs
        log_frame = tk.LabelFrame(bottom, text="AI Analysis & Rule Alerts")
        log_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.pack(fill="both", expand=True)

        # Data holder
        self.results_df = pd.DataFrame()

        # Initial load
        self.refresh_results()

    # ---------- Data helpers ----------

    def load_all_results(self):
        Path(RESULTS_DIR).mkdir(exist_ok=True)
        files = sorted(glob.glob(f"{RESULTS_DIR}/result_*.json"))
        rows = []
        for f in files:
            with open(f) as fp:
                j = json.load(fp)
            row = {
                "date": j["date"],
                "is_anomaly": j["is_anomaly"],
                "ai_score": j["ai_score"],
            }
            for k in FIELDS:
                row[k] = j["telemetry"].get(k)
            row["rule_alerts"] = j.get("rule_alerts", [])
            rows.append(row)
        if not rows:
            return pd.DataFrame(
                columns=["date"] + FIELDS + ["is_anomaly", "ai_score", "rule_alerts"]
            )
        df = pd.DataFrame(rows)
        df = df.sort_values("date").reset_index(drop=True)
        return df

    # ---------- UI updates ----------

    def refresh_results(self):
        self.results_df = self.load_all_results()
        if self.results_df.empty:
            self.status_label.config(text="Status: No results yet", fg="gray")
            self.date_combo["values"] = []
            self.clear_plot_and_table()
            return

        dates = self.results_df["date"].unique().tolist()
        self.date_combo["values"] = dates
        self.date_var.set(dates[-1])  # latest
        self.update_view_for_selected_date()
        self.update_overall_plot()

    def clear_plot_and_table(self):
        self.ax.clear()
        self.canvas.draw()
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.log_text.delete("1.0", tk.END)

    def update_overall_plot(self):
        if self.results_df.empty:
            return

        self.ax.clear()
        x = range(len(self.results_df))
        df = self.results_df

        if "battery_voltage" in df:
            self.ax.plot(x, df["battery_voltage"], label="Battery V")
        if "temperature" in df:
            self.ax.plot(x, df["temperature"], label="Temp C")
        if "cpu_usage" in df:
            self.ax.plot(x, df["cpu_usage"] / 10.0, label="CPU% /10")
        if "attitude_error" in df:
            self.ax.plot(x, df["attitude_error"], label="Attitude Err")

        # Mark anomalies
        if "is_anomaly" in df:
            anomaly_x = [i for i, v in enumerate(df["is_anomaly"]) if v]
            anomaly_y = [
                df["temperature"].iloc[i] for i in anomaly_x
            ] if "temperature" in df else [0] * len(anomaly_x)
            self.ax.scatter(
                anomaly_x, anomaly_y, color="red", label="Anomaly", zorder=5
            )

        self.ax.set_title("Telemetry Parameters Over Days (red = anomaly)")
        self.ax.set_xlabel("Day index")
        self.ax.legend()
        self.canvas.draw()

    def update_view_for_selected_date(self):
        if self.results_df.empty:
            return
        selected_date = self.date_var.get()
        if not selected_date:
            return

        day_df = self.results_df[self.results_df["date"] == selected_date]
        if day_df.empty:
            return
        row = day_df.iloc[0]

        status = "ANOMALY" if row["is_anomaly"] else "NORMAL"
        color = "red" if row["is_anomaly"] else "green"
        self.status_label.config(
            text=f"Status for {selected_date}: {status}", fg=color
        )

        # Table
        for r in self.tree.get_children():
            self.tree.delete(r)
        for k in FIELDS:
            val = row.get(k)
            text = f"{val:.2f}" if pd.notna(val) else "N/A"
            self.tree.insert("", tk.END, values=(k, text))

        # Logs
        self.log_text.delete("1.0", tk.END)
        self.log_text.insert(tk.END, f"Date: {selected_date}\n")
        self.log_text.insert(tk.END, f"AI score: {row['ai_score']:.4f}\n")
        self.log_text.insert(tk.END, f"Anomaly: {row['is_anomaly']}\n")
        alerts = row.get("rule_alerts") or []
        if alerts:
            self.log_text.insert(tk.END, "\nRule-based alerts:\n")
            for a in alerts:
                self.log_text.insert(tk.END, f"- {a}\n")
        else:
            self.log_text.insert(tk.END, "\nRule-based alerts: None\n")

    # ---------- Actions ----------

    def run_manual_test(self):
        try:
            self.status_label.config(text="Status: Running test...", fg="orange")
            self.root.update_idletasks()
            path, result = process_nightly(auto_generate=True)
            messagebox.showinfo("Test Complete", f"New result saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error during test:\n{e}")
        finally:
            self.refresh_results()


if __name__ == "__main__":
    root = tk.Tk()
    app = NightlyHealthGUI(root)
    root.mainloop()
