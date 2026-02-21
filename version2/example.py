import os
import pandas as pd
from spike_detector import SpikeDetector

csv_file = "XAUUSD_GMT+0_NO-DST_M1.csv"

if not os.path.exists(csv_file):
    print(f"Error: {csv_file} not found")
    exit(1)

# MT-style CSV has NO headers → force column names
df = pd.read_csv(
    csv_file,
    header=None,
    names=["date", "time", "open", "high", "low", "close", "volume"]
)

print("CSV columns:", df.columns.tolist())

# Ensure strings before joining
df["date"] = df["date"].astype(str)
df["time"] = df["time"].astype(str)

# Merge date + time safely
df["time"] = pd.to_datetime(
    df["date"] + " " + df["time"],
    format="%Y.%m.%d %H:%M:%S",
    errors="coerce"
)

# Remove old date column
df = df.drop(columns=["date"])

# Convert numeric columns
for col in ["open", "high", "low", "close", "volume"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Drop bad rows if parsing failed
df = df.dropna().reset_index(drop=True)

# Sort chronologically
df = df.sort_values("time").reset_index(drop=True)

# ---------------------------------------------------------
# CALCULATE POSITION INSIDE 4H CANDLE
# ---------------------------------------------------------
df["h4_start"] = df["time"].dt.floor("4h")
df["minute_in_h4"] = (df["time"] - df["h4_start"]).dt.total_seconds() / 60

# ---- Run spike detector ----
detector = SpikeDetector()
spikes = detector.detect_spikes(df)

print("Spikes found:", len(spikes))
print(spikes.head())

# ==========================================================
# SPIKES PER DAY ANALYSIS
# ==========================================================
# if len(spikes) > 0:

#     spikes["date"] = pd.to_datetime(spikes["time"]).dt.date
#     spikes_per_day = spikes.groupby("date").size()

#     print("\n--- Spike Statistics ---")
#     print("Total spikes:", len(spikes))
#     print("Days with spikes:", len(spikes_per_day))
#     print("Average spikes/day:", round(spikes_per_day.mean(), 2))
#     print("Median spikes/day:", spikes_per_day.median())
#     print("Max spikes/day:", spikes_per_day.max())
#     print("Min spikes/day:", spikes_per_day.min())

# ----------------------------------------
# DATA COVERAGE STATISTICS
# ----------------------------------------

# # Total unique calendar days in dataset
# total_days = df["time"].dt.date.nunique()

# # First and last timestamps
# start_date = df["time"].min()
# end_date = df["time"].max()

# # Total minutes of data
# total_minutes = len(df)

# # Expected minutes if continuous data
# expected_minutes = total_days * 1440

# print("\n--- Data Coverage ---")
# print("Start date:", start_date)
# print("End date:", end_date)
# print("Total calendar days:", total_days)
# print("Total M1 candles:", total_minutes)
# print("Expected minutes:", expected_minutes)
# print("Missing minutes:", expected_minutes - total_minutes)

# ==========================================================
# FAST ELBOW LOGIC TEST
# ==========================================================

reversal_events = []

opens = df["open"].values
closes = df["close"].values
times = df["time"].values

time_to_index = {t: i for i, t in enumerate(times)}

LOOKAHEAD = 60   # minutes to scan after spike (adjust if needed)

for _, spike in spikes.iterrows():

    spike_idx = time_to_index.get(spike["time"])
    if spike_idx is None:
        continue

    spike_dir = spike["direction"]

    elbow_double_occurred = False
    consecutive_opposing = 0

    # Only scan limited window after spike
    for j in range(spike_idx + 1, min(spike_idx + LOOKAHEAD, len(df))):

        is_red = closes[j] < opens[j]
        is_green = closes[j] > opens[j]

        opposing = (
            (spike_dir == "BULLISH" and is_red) or
            (spike_dir == "BEARISH" and is_green)
        )

        if opposing:
            consecutive_opposing += 1
        else:

            if consecutive_opposing == 2:

                if not elbow_double_occurred:
                    elbow_double_occurred = True
                else:
                    reversal_events.append({
                        "spike_time": spike["time"],
                        "reversal_time": times[j],
                        "direction": spike_dir
                    })
                    break

            consecutive_opposing = 0

reversals = pd.DataFrame(reversal_events)

print("\n--- Elbow Reversal Stats ---")
print("Reversals detected:", len(reversals))

if len(reversals) > 0:
    rate = len(reversals) / len(spikes) * 100
    print(f"Reversal rate: {rate:.2f}%")