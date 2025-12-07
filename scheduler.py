import time
from datetime import datetime

from nightly_processor import process_nightly

# Set your nightly run time (24-hour format)
TARGET_TIME = "23:30"  # e.g. 11:30 PM


def should_run(now_str, target_str):
    return now_str == target_str


if __name__ == "__main__":
    print("Simple nightly scheduler running... (checks every 30 seconds)")
    while True:
        now = datetime.now()
        now_str = now.strftime("%H:%M")
        if should_run(now_str, TARGET_TIME):
            print(f"Running nightly process at {now} ...")
            try:
                path, _ = process_nightly(auto_generate=True)
                print("Nightly result saved to", path)
            except Exception as e:
                print("Error during nightly processing:", e)
            time.sleep(60)  # avoid double run in same minute
        time.sleep(30)
