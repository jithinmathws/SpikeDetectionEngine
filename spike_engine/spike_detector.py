# spike_detector.py
import pandas as pd


# =========================
# CONFIG (MOVE TO config.py LATER)
# =========================
MIN_SPIKE_PIPS = {
    "XAUUSD": 50,
    "USDJPY": 15
}

MAX_OPPOSING_CANDLES = 2
MAX_NEUTRAL_CANDLES = 1


# =========================
# SPIKE DETECTION
# =========================
def detect_spikes(df: pd.DataFrame, symbol: str, pip_size: float):
    """
    Detect spike movements in M1 data.

    Parameters
    ----------
    df : pd.DataFrame
        Output of candle_utils.calculate_candle_metrics()
    symbol : str
        Trading symbol
    pip_size : float
        Pip size for symbol

    Returns
    -------
    list of dict
        Each dict represents a detected spike
    """

    spikes = []

    state = "IDLE"
    spike = None

    for i, row in df.iterrows():

        # ---------------------------------
        # RESET ON SESSION GAP
        # ---------------------------------
        if row["session_gap"]:
            if state == "TRACKING":
                finalize_spike(spike, spikes, pip_size, symbol)
            state = "IDLE"
            spike = None
            continue

        # ---------------------------------
        # STATE: IDLE
        # ---------------------------------
        if state == "IDLE":
            if row["direction"] in ("bull", "bear"):
                spike = initialize_spike(row, i)
                state = "TRACKING"
            continue

        # ---------------------------------
        # STATE: TRACKING
        # ---------------------------------
        if state == "TRACKING":
            update_spike(spike, row, i)

            # Count structure
            if row["direction"] == "neutral":
                spike["neutral_candles"] += 1
            elif row["direction"] != spike["direction"]:
                spike["opposing_candles"] += 1

            # Rule violations
            if (
                spike["opposing_candles"] > MAX_OPPOSING_CANDLES or
                spike["neutral_candles"] > MAX_NEUTRAL_CANDLES
            ):
                finalize_spike(spike, spikes, pip_size, symbol)
                state = "IDLE"
                spike = None
                continue

    # ---------------------------------
    # FINALIZE IF OPEN
    # ---------------------------------
    if state == "TRACKING":
        finalize_spike(spike, spikes, pip_size, symbol)

    return spikes


# =========================
# SPIKE HELPERS
# =========================
def initialize_spike(row, index):
    return {
        "start_index": index,
        "end_index": index,
        "start_time": row["time"],
        "end_time": row["time"],
        "direction": row["direction"],
        "high": row["high"],
        "low": row["low"],
        "candles": 1,
        "opposing_candles": 0,
        "neutral_candles": 0
    }


def update_spike(spike, row, index):
    spike["end_index"] = index
    spike["end_time"] = row["time"]
    spike["candles"] += 1
    spike["high"] = max(spike["high"], row["high"])
    spike["low"] = min(spike["low"], row["low"])
    spike["max_range"] = max(
        spike.get("max_range", 0),
        abs(spike["high"] - spike["low"])
    )


def is_in_final_hour_of_h4(timestamp):
    """
    Check if timestamp (UTC+8) is within the final 60 minutes
    before an H4 candle close.
    """
    hour = timestamp.hour
    h4_close_hours = [3, 7, 11, 15, 19, 23]

    for close_hour in h4_close_hours:
        if hour == (close_hour - 1) % 24:
            return True
    return False


def finalize_spike(spike, spikes, pip_size, symbol):
    MAX_SPIKE_MINUTES = 12  # try 10 or 15 later
    spike_size = abs(spike["high"] - spike["low"]) / pip_size
    
    if spike["candles"] > MAX_SPIKE_MINUTES:
        return

    if spike_size < MIN_SPIKE_PIPS[symbol]:
        return

    if spike["opposing_candles"] > 1:
        return
    
    
    spike["spike_pips"] = round(spike_size, 2)
    spike["duration_minutes"] = spike["candles"]
    avg_per_min = spike["spike_pips"] / spike["candles"]

    if avg_per_min < 5:  # pips per minute (tune per asset)
        return
    
    if spike["opposing_candles"] == 0:
        spike["elbow_type"] = "None"
    elif spike["opposing_candles"] == 1:
        spike["elbow_type"] = "Single"
    else:
        spike["elbow_type"] = "Double"

    # 🔑 CONTEXT FLAG
    spike["h4_final_hour"] = is_in_final_hour_of_h4(spike["start_time"])

    spikes.append(spike)

